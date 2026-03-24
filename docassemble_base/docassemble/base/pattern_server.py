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


async def _worker(queue):
    while True:
        request, future = await queue.get()
        try:
            module = getattr(docassemble_pattern, request[0])
            fn = getattr(module, request[1])
            result = fn(*request[2], **request[3])
            future.set_result({'result': result})
        except Exception:
            future.set_result({'error': traceback.format_exc()})


async def _handle(reader, writer, queue):
    try:
        while True:
            request = await _read_msg(reader)
            future = asyncio.get_event_loop().create_future()
            await queue.put((request, future))
            await writer.drain()
            response = await future
            await _write_msg(writer, response)
    except asyncio.IncompleteReadError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    queue = asyncio.Queue()
    asyncio.create_task(_worker(queue))
    server = await asyncio.start_unix_server(
        lambda r, w: _handle(r, w, queue),
        path=SOCKET_PATH,
    )
    async with server:
        await server.serve_forever()

asyncio.run(main())
