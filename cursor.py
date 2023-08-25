import os, openai
openai.api_key = os.environ.get('graysk')
models = openai.Model.list()
gpt4 = [x for x in [dict(d)['id'] for d in models['data']] if 'gpt-4' in x]
print('gpt-4 is here!' if len(gpt4) > 0 else 'gpt-4 :(')


'''
Step 1: Try generating with Cmd+K or Ctrl+K on a new line. Ask for CLI-based game of TicTacToe.
Step 2: Hit Cmd+L or Ctrl+L and ask the chat what the code does. 
   - Then, try running the code
Step 3: Try highlighting all the code with your mouse, then hit Cmd+k or Ctrl+K. 
   - Instruct it to change the game in some way (e.g. add colors, add a start screen, make it 4x4 instead of 3x3)
Step 4: To try out cursor on your own projects, go to the file menu (top left) and open a folder.

* Highlight code. Hit Cmd+K to prompt an edit.
* Open chat by clicking the right-bar button (on the top-right).
  - Highlight code and hit Cmd+Shift+L to focus the AI on particular pieces of code 
  - Try the "with codebase" button to ask about the entire repo
  - Use @ to import documentation
* Hover over a terminal error. Click "Auto-Debug".

generate edits, spot bugs, find code, learn about docs, and explain code.
'''



