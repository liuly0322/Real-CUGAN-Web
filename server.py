from fastapi import FastAPI, BackgroundTasks, UploadFile, File  # Fastapi
from fastapi.middleware.cors import CORSMiddleware  # 跨域调用
import uvicorn
from upcunet_v3 import *
import time
import cv2
from time import time as ttime
from datetime import date

from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory="outputs"), name="static")


def convert(filename: str, scale: int = 2):
    weight_path = ["weights_v3/up2x-latest-no-denoise.pth",
                   "weights_v3/up3x-latest-no-denoise.pth", "weights_v3/up4x-latest-no-denoise.pth"][scale - 2]
    tile_mode = 5
    cache_mode = 3
    alpha = 1
    weight_name = weight_path.split("/")[-1].split(".")[0]
    upscaler2x = RealWaifuUpScaler(
        scale, weight_path, half=False, device="cpu")
    input_dir = "%s/assets" % root_path
    output_dir = "%s/outputs" % root_path
    os.makedirs(output_dir, exist_ok=True)
    name = filename
    tmp = name.split(".")
    inp_path = os.path.join(input_dir, name)
    suffix = tmp[-1]
    prefix = ".".join(tmp[:-1])
    tmp_path = os.path.join(root_path, "tmp", "%s.%s" %
                            (int(time.time() * 1000000), suffix))
    print(inp_path, tmp_path)
    # 支持中文路径
    # os.link(inp_path, tmp_path)#win用硬链接
    os.symlink(inp_path, tmp_path)  # linux用软链接
    frame = cv2.imread(tmp_path)[:, :, [2, 1, 0]]
    t0 = ttime()
    result = upscaler2x(frame, tile_mode=tile_mode,
                        cache_mode=cache_mode, alpha=alpha)[:, :, ::-1]
    t1 = ttime()
    print(prefix, "done", t1 - t0, "tile_mode=%s" % tile_mode, cache_mode)
    tmp_opt_path = os.path.join(root_path, "tmp", "%s.%s" % (
        int(time.time() * 1000000), suffix))
    cv2.imwrite(tmp_opt_path, result)
    final_opt_path = os.path.join(output_dir, prefix + ".png")
    os.rename(tmp_opt_path, final_opt_path)
    os.remove(tmp_path)


@app.post("/upload")
async def recv_file(file: UploadFile, passwd: str, scale: int, background_tasks: BackgroundTasks):
    # 解析参数，确保合法
    if scale not in [2, 3, 4]:
        return {"error": "invalid scale"}
    if passwd != "passwd-here-please":
        return {"error": "wrong passwd"}
    # 保存到服务器本地文件
    file_data = await file.read()
    # 将文件名和时间哈希
    filename = f"{date.today()}-{hash(file.filename + str(ttime()))}"
    suffix = os.path.splitext(file.filename)[-1]
    with open(f"assets/{filename + suffix}", "wb") as fp:
        fp.write(file_data)
    fp.close()
    # 后台任务用于生成放大后文件
    background_tasks.add_task(convert, filename + suffix, scale)
    # 返回 url
    rt_msg = {
        "name": filename,
    }
    return rt_msg
