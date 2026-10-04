### Streamlink Megogo plugin

---

### Setup:
- Download [the plugin file](https://github.com/YupCore/streamlink_megogo/blob/main/megogo.py).
- Clone [streamlink](https://github.com/streamlink/streamlink) via git (or download via Code->Zip, then extract to a directory).
- Open your directory.
- Copy the plugin .py file into `src/streamlink/plugins/`(this will sideload the plugin).
- Go back to the root of your directory(leave `src/streamlink/plugins/` chain).
- Open your command line utility of choice & run streamlink via `python -m streamlink_cli "your_megogo_link" best --http-cookies-file "your_megogo_cookies.txt"` command.

---

### Questions

## How to get cookies?
I recommend using [this extension](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc?hl=en), as it's very straightforward.
Download it, open megogo.net(with your account logged on) and then open the extension, click "Export As"(not export all!) and now you have your cookies.
Place the .txt file wherever and just pass the path to it via --http-cookies-file argument.

***Do NOT share those cookies anywhere, as you might get your account hacked.***

Read the errors, if it mentions anything about authentication failure, your cookies probably expired — redownload them.

## How do I know if this is safe?
Open the file, read the code, or send it to an LLM(like chatgpt or claude) and ask about it if you're unsure.

---

For help with streamlink itself, refer to the official [streamlink documentation](https://streamlink.github.io/cli.html).
