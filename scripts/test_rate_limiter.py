"""Real Redis regression checks in a disposable loopback-only server.

Uses Python's standard library. Does not connect to the user's existing Redis.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import os
import platform
import socket
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]


class RedisError(Exception):
    pass


def command(port, *args):
    values = [str(arg).encode('utf-8') for arg in args]
    request = b'*%d\r\n' % len(values)
    request += b''.join(b'$%d\r\n' % len(v) + v + b'\r\n' for v in values)
    with socket.create_connection(('127.0.0.1', port), timeout=5) as connection:
        connection.sendall(request)
        stream = connection.makefile('rb')
        prefix, value = stream.read(1), stream.readline().rstrip(b'\r\n')
        if prefix == b'-':
            raise RedisError(value.decode())
        if prefix == b':':
            return int(value)
        if prefix == b'+':
            return value.decode()
        if prefix == b'$':
            return None if int(value) == -1 else stream.read(int(value)).decode()
        raise RedisError('Unexpected response')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--redis-server', required=True)
    parser.add_argument('--output', default='')
    args = parser.parse_args()
    executable = Path(args.redis_server).resolve()
    if not executable.is_file():
        raise SystemExit('Redis server executable not found')
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    runtime = ROOT / '.local'
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='limiter-', dir=runtime) as directory:
        folder = Path(directory)
        config = folder / 'redis.conf'
        config.write_text('bind 127.0.0.1\nport %d\nsave ""\nappendonly no\n'
                          'dir "%s"\nlogfile "%s"\n' %
                          (port, folder.as_posix(), (folder/'redis.log').as_posix()), encoding='utf-8')
        process = subprocess.Popen([str(executable), str(config)], cwd=folder,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        try:
            deadline = time.monotonic() + 10
            while True:
                try:
                    if command(port, 'PING') == 'PONG':
                        break
                except (OSError, RedisError):
                    if process.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError('Disposable Redis failed to start')
                    time.sleep(0.05)
            version = next(line.split(':', 1)[1] for line in command(port, 'INFO', 'server').splitlines()
                           if line.startswith('redis_version:'))
            old = (ROOT/'src/test/resources/limiter-legacy.lua').read_text(encoding='utf-8')
            fixed = (ROOT/'src/main/resources/limiter.lua').read_text(encoding='utf-8')
            prefix, now, results = 'locallife:test:' + uuid.uuid4().hex + ':', int(time.time()*1000), []

            def evaluate(script, key, window, limit, stamp, member=None):
                values = [script, 1, prefix+key, window, limit, stamp]
                if member is not None:
                    values.append(member)
                return command(port, 'EVAL', *values)

            def check(name, condition, **observed):
                results.append(dict(test=name, passed=bool(condition), **observed))
                if not condition:
                    raise AssertionError(json.dumps(results[-1]))

            old_results = [evaluate(old, 'old', 60, 10, now) for _ in range(200)]
            count = sum(x > 0 for x in old_results)
            check('legacy_same_millisecond_defect', count > 10,
                  requests=200, limit=10, accepted=count, records=command(port, 'ZCARD', prefix+'old'))
            new_results = [evaluate(fixed, 'fixed', 60, 10, now, uuid.uuid4().hex) for _ in range(200)]
            count = sum(x > 0 for x in new_results)
            check('fixed_same_millisecond', count == 10 and command(port, 'ZCARD', prefix+'fixed') == 10,
                  requests=200, limit=10, accepted=count)
            with ThreadPoolExecutor(max_workers=20) as pool:
                concurrent_results = list(pool.map(
                    lambda _: evaluate(fixed, 'parallel', 60, 25, now, uuid.uuid4().hex), range(200)))
            count = sum(x > 0 for x in concurrent_results)
            check('concurrent_same_millisecond', count == 25 and command(port, 'ZCARD', prefix+'parallel') == 25,
                  requests=200, workers=20, limit=25, accepted=count)
            boundary = [evaluate(fixed, 'edge', 1, 1, now+offset, str(offset)) for offset in [0, 999, 1000]]
            check('window_boundary', boundary == [1, 0, 1], responses=boundary)
            check('independent_keys', evaluate(fixed, 'other', 60, 1, now, 'one') == 1)
            ttl = command(port, 'PTTL', prefix+'other')
            check('key_expiry', 0 < ttl <= 60000, ttl_ms=ttl)
            errors = 0
            invalid = [(0, 1, now, 'a'), (1, 0, now, 'b'), (1.5, 1, now, 'c'),
                       (1, 1, -1, 'd'), (1, 1, now, '')]
            for values in invalid:
                try:
                    evaluate(fixed, 'invalid', *values)
                except RedisError:
                    errors += 1
            check('invalid_arguments', errors == len(invalid) and command(port, 'EXISTS', prefix+'invalid') == 0,
                  rejected=errors)
            report = dict(platform=platform.system(), redis_version=version,
                          scope='Redis script correctness, not HTTP throughput or application integration', results=results)
            if args.output:
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            print(json.dumps(report, ensure_ascii=False))
        finally:
            if process.poll() is None:
                try:
                    command(port, 'SHUTDOWN', 'NOSAVE')
                except (OSError, RedisError):
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=5)


if __name__ == '__main__':
    main()
