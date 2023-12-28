# pip install streamlit
# 실행 : streamlit run AI-Blog-Writer.py // streamlit run [사용자지정 이름].py
# streamlit : 계정 당 3개 앱까지만 실행 무료
# 

import re
import zipfile
import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime, timedelta

prompt = f'''Write blog posts in markdown format.\n
Write the theme of your blog as <<TOPIC>> and its category is <<CATEGORY>>.\n
And write an entire blog within <<LETTERS>> characters.\n
Include the helpful information as a list style.\n
Highlight, bold, or italicize important words or sentences.\n
The audience of this article is 20-40 years old.\n
Create several hashtags and add them only at the end of the line.\n
Add a summary of the entire article at the beginning of the blog post.'''

def write_blog(prompt, prompt_add):
    prompt_final = prompt + prompt_add
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt_final}
        ],
    )

    body = result.choices[0].message.content

    tags = extract_tags(body)

    header = make_header(topic=topic, category=category, tags=tags)

    output = header + body

    today = datetime.now()
    timestring = today.strftime('%Y-%m-%d')
    filename = f"{timestring}-{'-'.join(topic.lower().split())}.md"
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(output)
        f.close()
    return filename

def extract_tags(body):
    hashtag_pattern = r'(#+[a-zA-Z0-9(_)]{1,})'
    hashtags = [w[1:] for w in re.findall(hashtag_pattern, str(body))]
    hashtags = list(set(hashtags))
    tag_string = ""
    for w in hashtags:
        if len(w) > 3:
            tag_string += f'{w}, '
    tag_string = re.sub(r'[^a-zA-Z, ]', '', tag_string)
    tag_string = tag_string.strip()[:-1]
    return tag_string

def make_header(topic, category, tags):
    page_head = f'''---
layout: single
title:  "{topic}"
categories: {category}
tag: [{tags}]
--- \n '''
    return page_head

def get_file(filename):
    with open(filename, 'r') as f:
        data = f.read()
    return data

def make_prompt(prompt, topic='<<TOPIC>>', category='<<CATEGORY>>', letters='<<LETTERS>>'):
    if topic:
        prompt = prompt.replace('<<TOPIC>>', topic)
    if category:
        prompt = prompt.replace('<<CATEGORY>>', category)
    if letters:
        prompt = prompt.replace('<<LETTERS>>', str(letters))
    return prompt

st.title("AI를 활용한 블로그 자동 글쓰기 프로그램 - ver 0.1")
st.info("**#1 단계** : https://beta.openai.com 가입 후, 발급받은 API KEY를 아래 칸에 입력")

value=''
apikey = st.text_input(label='OPENAI API 키', placeholder='OPENAI API키를 입력', value=value)

if apikey:
    st.markdown(f'OPENAI API키 \" `{apikey}` \" 가 맞는지 꼭 확인!!')
    client = OpenAI(api_key = apikey)
    st.info("**#2 단계** : 글의 주제 입력 ( 영어로 입력 추천 ) ")
    topic = st.text_input(label='글의 주제', placeholder=' 예시 : Top 10 cheap hotels in Paris')
    if topic:
        st.info("**#3 단계** : 글의 카테고리 입력 ( 영어로 입력 추천 ) ")
        category = st.text_input(label='글의 카테고리', placeholder=' 예시 : Travel ')
        if category:
            st.info("**#4 단계** : 글의 생성 분량을 입력")
            letters = st.number_input(label='글의 생성 분량', value=None, min_value=100, max_value=2000, placeholder=' 100~2000자 사이 숫자로 입력 ')
            if letters:
                st.info("**#5 단계** : 최종 지시사항 확인 후, 생성 버튼 클릭 ( 생성시간은 AI상황에 따라 다름 )")
                button = st.button('생성하기')
                prompt = make_prompt(prompt=prompt, topic=topic, category=category, letters=letters)
                st.markdown(f'**최종 지시사항** : {prompt} ')
                st.warning("필요시, 추가 지시사항 입력 가능 ( 영어로 입력 추천 )")
                prompt_add = st.text_area(label='추가 지시사항', placeholder='예시 : To enhance creativity, randomness, diversity, emotion and empathy and lower the consistency in the writing.', height=200)
                if button:
                    filename = write_blog(prompt=prompt, prompt_add=prompt_add)
                    download_btn = st.download_button(label='생성글 다운로드 ( 마크다운 형식 ) ', 
                                                data=get_file(filename=filename),
                                                file_name=filename,
                                                mime='text/markdown')
