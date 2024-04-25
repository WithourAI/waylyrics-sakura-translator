# Waylyrics 歌词翻译插件

这是一个针对 Waylyrics 的插件，可以获取 Waylyrics 缓存的歌词文件，并利用 [SakuraLLM](https://github.com/SakuraLLM/Sakura-13B-Galgame) 将其中的日文歌词翻译为中文。

## 功能特点

- 自动获取 Waylyrics 缓存的歌词文件
- 利用 SakuraLLM 将日文歌词翻译为中文
- 方便地查看和欣赏歌词的中文翻译

## 使用方法

1. 启动 SakuraLLM 本地服务器，有两种方法可供选择：
  - 使用 SakuraLLM 的官方启动器
  - 下载 SakuraLLM 的模型文件，然后使用 [llama.cpp](https://github.com/ggerganov/llama.cpp) 启动本地服务器：
    ```
    ./server -m /path/to/sakura-13b-lnovel-v0.9b-Q6_K.gguf -c 1024 -ngl 99 -cb
    ```

2. 确保本地服务器的 API 地址为 `http://127.0.0.1:8080/v1/`。如有需要，可以自行更改地址和端口

3. 下载本项目的源代码，并安装依赖：
    ```python
   git clone https://github.com/WithourAI/waylyrics-sakura-translator.git
   cd waylyrics-sakura-translator
   pip install -r requirements.txt
   ```

4. 启动 Waylyrics 歌词翻译插件
    ```python
   python main.py
   ```

5. 播放音乐并享受歌词的中文翻译吧！

## 注意事项

- 请确保 SakuraLLM 本地服务器正常运行并可访问
- 目前，程序已将 API 地址硬编码为 `http://127.0.0.1:8080/v1/`。如果您需要更改地址和端口，请相应地修改程序
- 本插件依赖于 Waylyrics 缓存的歌词文件，请确保 Waylyrics 正常工作并缓存了相应的歌词文件

## 贡献

欢迎提供反馈和贡献代码！如果您发现任何问题或有改进建议，请随时提交 Issue 或 Pull Request。

## 致谢

- [SakuraLLM](https://github.com/SakuraLLM/Sakura-13B-Galgame) - 提供了强大的日文到中文翻译模型。
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - 提供了简便的模型服务器启动方式。
- [Waylyrics](https://github.com/waylyrics/waylyrics) - 提供了Linux操作系统下歌词下载和展示的功能。
- [PiDanShouRouZhouXD](https://github.com/PiDanShouRouZhouXD) - 提供了SakuraLLM输出的相关处理代码。

## 许可证

本项目基于 [MIT 许可证](LICENSE) 发布。