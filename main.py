

import discord

import requests

import base64

from PIL import Image

from io import BytesIO

import os

token = '' #봇토큰

api_key = '' #발급한 API키

ROLE = 0 #역할 아이디

ADMINISTRATORS = [] #관리자들

client = discord.Client()


@client.event
async def on_message(msg):

    if msg.author.bot:
        return False

    if msg.author.id in ADMINISTRATORS:

        if msg.content == '!verify':
            
            view = discord.ui.View()
            item = discord.ui.Button(style=discord.ButtonStyle.blurple, label="인증", custom_id='verify')
            view.add_item(item=item)
           

            await msg.channel.send(embed=discord.Embed(title='아래 버튼을 눌러 인증해주세요.', description='개인정보를 수집하지 않습니다.'), view=view)


@client.event
async def on_interaction(inter):
    
    if (inter.data['custom_id'] == 'verify'):

        await inter.user.send('통신사를 입력해주세요.')

        co = await client.wait_for('message', check=lambda m: m.author.id == inter.user.id and isinstance(m.channel, discord.DMChannel))

        first = requests.post('http://bankapi.lol:8880/send', json={'co' : co.content.upper(), 'key': api_key})


        

        await inter.user.send('이름을 입력해주세요.')

        name = await client.wait_for('message', check=lambda m: m.author.id == inter.user.id and isinstance(m.channel, discord.DMChannel), timeout=60)
        
        await inter.user.send('생년월일를 입력해주세요.')

        mynum1 = await client.wait_for('message', check=lambda m: m.author.id == inter.user.id and isinstance(m.channel, discord.DMChannel), timeout=60)

        await inter.user.send('주민등록번호 첫자리를 입력해주세요.')

        mynum2 = await client.wait_for('message', check=lambda m: m.author.id == inter.user.id and isinstance(m.channel, discord.DMChannel), timeout=60)

        await inter.user.send('전화번호를 입력해주세요.')

        econum = await client.wait_for('message', check=lambda m: m.author.id == inter.user.id and isinstance(m.channel, discord.DMChannel), timeout=60)

        im = Image.open(BytesIO(base64.b64decode(first.json()['image'])))

        im.save(f'{inter.user.id}.png')

        await inter.user.send('아래 보이는 캡차를 입력해주세요.', file=discord.File(f'{inter.user.id}.png'))

        os.remove(f'{inter.user.id}.png')

        text = await client.wait_for('message', check=lambda m: m.author.id == inter.user.id and isinstance(m.channel, discord.DMChannel), timeout=60)

        # https://user-images.githubusercontent.com/79750848/219383868-fbf84e75-66be-4dab-82fe-3832825e420b.png

        second = requests.post('http://bankapi.lol:8880/solve', json={'name' : name.content,
                                                            'mynum1': mynum1.content, 
                                                            'mynum2' : mynum2.content,
                                                            'econum': econum.content,
                                                            'task': first.json()['taskID'],
                                                            'text': text.content,
                                                            'key' : api_key}) # text: 위 캡차에 쓰여져 있는 번호

        await inter.user.send('휴대폰으로 간 인증번호를 3분안에 입력해주세요.')

        authnumber = await client.wait_for('message', check=lambda m: m.author.id == inter.user.id and isinstance(m.channel, discord.DMChannel), timeout=180)
                                                            
        
        third = requests.post('http://bankapi.lol:8880/finish', json={
                                                            'task': first.json()['taskID'],
                                                            'authnumber': authnumber.content,
                                                            'key': api_key}) #authnumber: 입력한 휴대폰 번호로 간 인증번호



        result = third.json()

        if result['auth']:

            await inter.user.add_roles ( inter.guild.get_role(ROLE) )
            await inter.user.send('인증이 성공되었습니다.\n인증을 진행하신 서버를 확인해주세요.')
        else:
            await inter.user.send('인증 실패')

client.run(token)