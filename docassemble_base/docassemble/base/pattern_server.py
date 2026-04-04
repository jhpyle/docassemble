import asyncio
import struct
import traceback
import os
import nltk
import msgpack

try:
    if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'omw-1.4.zip')):
        nltk.download('omw-1.4')
except:
    pass
try:
    if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'wordnet.zip')):
        nltk.download('wordnet')
except:
    pass
try:
    if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'wordnet_ic.zip')):
        nltk.download('wordnet_ic')
except:
    pass
try:
    if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'sentiwordnet.zip')):
        nltk.download('sentiwordnet')
except:
    pass
import docassemble_pattern.en  # pylint: disable=import-error,no-name-in-module
import docassemble_pattern.es  # pylint: disable=import-error,no-name-in-module
import docassemble_pattern.de  # pylint: disable=import-error,no-name-in-module
import docassemble_pattern.fr  # pylint: disable=import-error,no-name-in-module
import docassemble_pattern.it  # pylint: disable=import-error,no-name-in-module
import docassemble_pattern.nl  # pylint: disable=import-error,no-name-in-module

SOCKET_PATH = os.environ.get('NLTKSOCKET', '/var/run/nltk/da_nltk.sock')


async def _read_msg(reader):
    header = await reader.readexactly(4)
    n = struct.unpack('>I', header)[0]
    return msgpack.unpackb(await reader.readexactly(n))


async def _write_msg(writer, obj):
    data = msgpack.packb(obj)
    writer.write(struct.pack('>I', len(data)) + data)
    await writer.drain()


def _call(request):
    module = getattr(docassemble_pattern, request[0])
    fn = getattr(module, request[1])
    return fn(*request[2], **request[3])


async def _handle(reader, writer):
    try:
        while True:
            request = await _read_msg(reader)
            try:
                result = await asyncio.to_thread(_call, request)
                await _write_msg(writer, {'result': result})
            except Exception:
                await _write_msg(writer, {'error': traceback.format_exc()})
    except asyncio.IncompleteReadError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_unix_server(
        _handle,
        path=SOCKET_PATH,
    )
    async with server:
        await server.serve_forever()

asyncio.run(main())
