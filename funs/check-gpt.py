import os, openai
openai.api_key = os.environ.get('graysk')
models = openai.Model.list()
gpt4 = [x for x in [dict(d)['id'] for d in models['data']] if 'gpt-4' in x]
print('gpt-4 is here!' if len(gpt4) > 0 else 'gpt-4 :(')

print([x for x in [dict(d)['id'] for d in models['data']] if 'gpt' in x])


'''
* Open chat by clicking the right-bar button (on the top-right).
  - Highlight code and hit Cmd+Shift+L to focus the AI on particular pieces of code 
  - Try the "with codebase" button to ask about the entire repo
  - Use @ to import documentation
'''
