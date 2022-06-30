# Real-CUGAN-Web

Why this?

[Real-CUGAN](https://github.com/bilibili/ailab/tree/main/Real-CUGAN) is an amazing project for anime image super resolution

There is already a [web version](https://github.com/hanFengSan/realcugan-ncnn-webassembly) using webassembly based on ncnn, and it's really fast. I recommend you using this if you need

This project is designed only to run on server without gpu, and it's slow. Basically it is just a demo about background task in fastapi and fileuploader with vue2.

You may see the front-end [here](http://home.ustc.edu.cn/~liuly0322/cugan/)

## config

config about passwd is in `server.py`

modify your server ip in `index.html`

## deploy

requirements: torch, opencv, ...

```bash
uvicorn main:app --host 0.0.0.0 --port 80	# change to your port
```
