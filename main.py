import os
import base64
from aiohttp import web
import motor.motor_asyncio
import random
import string



client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://root:example@{os.environ.get('DB_HOST', 'localhost')}:27017")
db = client['redirecter']
collection = db['redirects']

async def index_page(request):
    return web.Response(text='''
                <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Redirecter</title>
            </head>
            <body>
            <h1>Redirecter</h1>
            <p>Redirects to a long URL based on a short URL,</p>
            <form action="/" method="post">
                <input type="text" name="lond_url" placeholder="Long URL" id="long_url" required>
                <input type="submit" value="make it short">
            </form>
            </body>
            </html>
    ''',
                        content_type='text/html')


async def receive_url(request):
    data = await request.post()
    long_url = data['lond_url']
    generate_resourse_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    document = await collection.insert_one(
        {'long_url': long_url,
         'resourse_id': generate_resourse_id})
    return web.Response(text=generate_resourse_id,
                        content_type='text/plain')


async def redirecter(request):
    resource_id = request.match_info['resource_id']

    document = await collection.find_one({'resource_id': resource_id})
    if document is None:
        return web.Response(text='Not found', status=404)

    long_url = document['long_url']
    return web.HTTPFound(long_url)




app = web.Application()
app.add_routes([web.get('/', index_page)])   #регистрация єндпотнтов (можно декоратором на хендлер)
app.add_routes([web.post('/', receive_url)])   #регистрация єндпотнтов (можно декоратором на хендлер)
app.add_routes([web.get('/{resource_id}', redirecter)])

web.run_app(app)



