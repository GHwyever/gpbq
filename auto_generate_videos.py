"""
高攀不起 - 全自动视频生成脚本
使用 Canvas Seedance 本地版 API，自动生成三集全部镜头视频

使用方法：
1. 确保本机已启动 Seedance 本地版（127.0.0.1:8787）
2. 将 all_frames.zip 解压到脚本同目录（会自动检测）
3. 填入 J 卡号（第 30 行）
4. python auto_generate_videos.py

依赖：pip install requests
"""

import requests
import os
import json
import time
import sys

# ======================== 配置 ========================
BASE_URL = "http://127.0.0.1:8787"
J_CARD_NO = "填入你的J卡号"  # ← ← ← 在这里填入

# 输出目录
OUTPUT_DIR = "./output_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 图片目录（解压后）
FRAMES_BASE = "./all_frames"

# 并发数（同时生成几个任务）
CONCURRENT = 2

# 每集的镜头定义：episode, shot, first_frame_path, last_frame_path, prompt, aspect_ratio
# prompt 末尾写 "总时长XX秒" 控制时长
EPISODES = [
    # ============ EP01（8镜头，每镜头15秒）============
    {
        "episode": "EP01",
        "shots": [
            {
                "shot": "Shot1",
                "first": "ep01/ep01_shot1_firstframe.png",
                "last": "ep01/ep01_shot1_lastframe.png",
                "prompt": "Cinematic aerial establishing shot of ancient Chinese capital city Yong'an at night during heavy snowfall, thousands of warm orange lanterns glowing, slowly zooming in toward the grand celebration mansion. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot2",
                "first": "ep01/ep01_shot2_firstframe.png",
                "last": "ep01/ep01_shot2_lastframe.png",
                "prompt": "Grand banquet hall with hundreds of guests celebrating engagement, red silk decorations, warm golden candlelight, camera slowly panning across the festive scene toward the marriage document stand. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot3",
                "first": "ep01/ep01_shot3_firstframe.png",
                "last": "ep01/ep01_shot3_lastframe.png",
                "prompt": "Desolate back gate of mansion in winter, dead trees, cold moonlight, transition to woman in red bridal robes holding torch approaching massive iron door, dramatic backlighting. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot4",
                "first": "ep01/ep01_shot3_lastframe.png",  # 共享 Shot 3 尾帧
                "last": "ep01/ep01_shot4_lastframe.png",
                "prompt": "Woman in red bridal robes descending narrow ice-covered stone staircase into underground ice cellar, torch light illuminating blue ice walls, descending deeper into darkness. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot5",
                "first": "ep01/ep01_shot5_firstframe.png",
                "last": "ep01/ep01_shot5_lastframe.png",
                "prompt": "Ice bed detail shot with jade bowl and golden needles, then woman in red bridal gown enters through doorway, her face revealed for the first time, tender yet sorrowful expression. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot6",
                "first": "ep01/ep01_shot6_firstframe.png",
                "last": "ep01/ep01_shot6_lastframe.png",
                "prompt": "Pale young man lying unconscious on transparent ice bed with iron shackles, warm brazier light, camera slowly tilts up to reveal ventilation grate with a human shadow passing by. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot7",
                "first": "ep01/ep01_shot7_firstframe.png",
                "last": "ep01/ep01_shot7_lastframe.png",
                "prompt": "Woman in red bridal robes walks toward ice bed, kneels beside unconscious man, gently wipes his forehead with silk handkerchief, intimate tender moment with warm firelight. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot8",
                "first": "ep01/ep01_shot8_firstframe.png",
                "last": "ep01/ep01_shot8_lastframe.png",
                "prompt": "Young man on ice bed with serene smile, then cut to woman sitting before bronze mirror in dimly lit room, adjusting hairpin, sorrowful expression reflected in mirror, cold moonlight through window. 总时长15秒",
                "ratio": "16:9"
            },
        ]
    },
    # ============ EP02（6镜头，每镜头15秒）============
    {
        "episode": "EP02",
        "shots": [
            {
                "shot": "Shot1",
                "first": "ep02/ep02_shot1_firstframe.png",
                "last": "ep02/ep02_shot1_lastframe.png",
                "prompt": "Woman in red bridal robes turns back to look at ice cellar interior with tearful eyes, then massive iron door slowly closes, warm light vanishing. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot2",
                "first": "ep02/ep02_shot2_firstframe.png",
                "last": "ep02/ep02_shot2_lastframe.png",
                "prompt": "Iron door closing from inside ice cellar, last sliver of warm light narrowing to nothing, then complete darkness with only dying brazier glow, frost spreading. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot3",
                "first": "ep02/ep02_shot3_firstframe.png",
                "last": "ep02/ep02_shot3_lastframe.png",
                "prompt": "Young man lying peacefully on ice bed with serene smile, camera tilts up to ventilation grate where warm light and a servant silhouette briefly appears. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot4",
                "first": "ep02/ep02_shot4_firstframe.png",
                "last": "ep02/ep02_shot4_lastframe.png",
                "prompt": "Elderly servant woman crouching in shock by ventilation grate, then cut to woman in red bridal robes coldly pouring dark liquid into bronze brazier, split composition showing master-servant dynamic. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot5",
                "first": "ep02/ep02_shot5_firstframe.png",
                "last": "ep02/ep02_shot5_lastframe.png",
                "prompt": "Woman in red bridal robes stands by carved wooden window in moonlight, looking at marriage document with sorrowful expression, then document burns in bronze brazier, ashes floating upward. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot6",
                "first": "ep02/ep02_shot6_firstframe.png",
                "last": "ep02/ep02_shot6_lastframe.png",
                "prompt": "Ventilation grate being sealed with iron plate, last warm light disappearing from ice cellar, then brazier flames slowly dying, frost spreading, fading to complete darkness. 总时长15秒",
                "ratio": "16:9"
            },
        ]
    },
    # ============ EP03（6镜头，每镜头15秒）============
    {
        "episode": "EP03",
        "shots": [
            {
                "shot": "Shot1",
                "first": "ep03/ep03_shot1_firstframe.png",
                "last": "ep03/ep03_shot1_lastframe.png",
                "prompt": "Complete darkness in ice cellar, young man lying unconscious, then eyes suddenly snap open with shock and disbelief, pupils constricted, dramatic awakening moment. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot2",
                "first": "ep03/ep03_shot1_lastframe.png",  # 共享 Shot 1 尾帧
                "last": "ep03/ep03_shot2_lastframe.png",
                "prompt": "Close-up of young man's face, eyes wide with sorrow, subtle tears forming at corners of eyes, tears crystallizing into ice crystals on cheeks in extreme cold, restrained emotional portrayal. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot3",
                "first": "ep03/ep03_shot3_firstframe.png",
                "last": "ep03/ep03_shot3_lastframe.png",
                "prompt": "Golden rune glowing on man's chest, consciousness transitions to cosmic void space with galaxy and nebulae, man floating horizontally, two luminous paths appearing: white reincarnation gate and golden-black flame path. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot4",
                "first": "ep03/ep03_shot4_firstframe.png",
                "last": "ep03/ep03_shot4_lastframe.png",
                "prompt": "Back in ice cellar, young man grits teeth and clenches fists with determination, iron chains pulling tight, close-up of chained hands gripping, will to survive. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot5",
                "first": "ep03/ep03_shot5_firstframe.png",
                "last": "ep03/ep03_shot5_lastframe.png",
                "prompt": "Cosmic consciousness space, ancient deity dissolving into golden light particles flowing toward floating man, then back to ice cellar, golden rune blazing on chest, energy spreading. 总时长15秒",
                "ratio": "16:9"
            },
            {
                "shot": "Shot6",
                "first": "ep03/ep03_shot5_lastframe.png",  # 共享 Shot 5 尾帧
                "last": "ep03/ep03_shot6_lastframe.png",
                "prompt": "Young man eyes closed with golden rune glowing, teeth clenched, then eyes burst open revealing striking golden-black heterochromatic eyes, ice surface cracking with energy wave, climactic awakening. 总时长15秒",
                "ratio": "16:9"
            },
        ]
    },
]

# ======================== 工具函数 ========================

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def api_get(path):
    r = requests.get(f"{BASE_URL}{path}", timeout=30)
    return r.json()

def api_post(path, json_data=None, files=None):
    if files:
        r = requests.post(f"{BASE_URL}{path}", files=files, timeout=60)
    else:
        r = requests.post(f"{BASE_URL}{path}", json=json_data, timeout=30)
    return r.json()

def check_health():
    try:
        d = api_get("/api/health")
        if d.get("ok"):
            log("✅ Seedance 本地版已连接")
            return True
    except:
        pass
    log("❌ 无法连接 Seedance 本地版，请确保已启动 (127.0.0.1:8787)")
    return False

def login():
    log(f"🔐 J卡登录: {J_CARD_NO[:4]}****{J_CARD_NO[-4:]}")
    d = api_post("/api/yunji-license/login", {"card_no": J_CARD_NO})
    if d.get("ok") or d.get("token"):
        log("✅ J卡登录成功")
        return True
    log(f"⚠️ 登录返回: {json.dumps(d, ensure_ascii=False)[:200]}")
    return True  # 可能已登录过

def purchase_session_pack():
    log("📦 拉取账号包...")
    d = api_post("/api/remote-session-pack/purchase-import", {
        "quantity": CONCURRENT,
        "product_id": "e6ec85c7-379a-4a61-9e46-f69bd385ab8d"
    })
    log(f"  结果: {json.dumps(d, ensure_ascii=False)[:200]}")
    return d

def upload_image(filepath):
    """上传图片到 Canvas，返回 URL"""
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        d = api_post("/api/assets/upload", files={"file": (filename, f)})
    url = d.get("url") or d.get("data", {}).get("url")
    if url:
        log(f"  上传成功: {filename} → {url[:60]}...")
        return url
    log(f"  ⚠️ 上传返回: {json.dumps(d, ensure_ascii=False)[:200]}")
    return None

def submit_video(prompt, first_url, last_url, ratio="16:9"):
    """提交视频生成任务（带首尾帧）"""
    nodes = [
        {
            "id": "prompt-1",
            "type": "prompt",
            "data": {"prompt": prompt}
        },
        {
            "id": "ref-first",
            "type": "referenceImage",
            "data": {
                "asset": {"type": "image", "name": "first_frame.png", "url": first_url}
            }
        },
        {
            "id": "ref-last",
            "type": "referenceImage",
            "data": {
                "asset": {"type": "image", "name": "last_frame.png", "url": last_url}
            }
        },
        {
            "id": "seedance-1",
            "type": "seedance",
            "data": {
                "modelType": "Standard",
                "resolution": "720p",
                "duration": "auto",
                "aspectRatio": ratio,
                "generateAudio": False,
                "randomSeed": True
            }
        }
    ]
    edges = [
        {"source": "prompt-1", "target": "seedance-1", "sourceHandle": "prompt", "targetHandle": "prompt"},
        {"source": "ref-first", "target": "seedance-1", "sourceHandle": "image", "targetHandle": "reference_1"},
        {"source": "ref-last", "target": "seedance-1", "sourceHandle": "image", "targetHandle": "reference_2"},
    ]
    d = api_post("/api/run", {"graph": {"nodes": nodes, "edges": edges}})
    return d

def poll_tasks():
    """查询所有任务状态"""
    return api_get("/api/tasks")

def download_video(task_id, output_path):
    """下载完成的视频"""
    r = requests.get(f"{BASE_URL}/api/tasks/{task_id}/download", timeout=120)
    if r.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(r.content)
        return True
    return False

# ======================== 主流程 ========================

def process_shot(episode_name, shot_info):
    """处理单个镜头：上传 → 提交 → 轮询 → 下载"""
    shot = shot_info["shot"]
    first_path = os.path.join(FRAMES_BASE, shot_info["first"])
    last_path = os.path.join(FRAMES_BASE, shot_info["last"])
    ratio = shot_info["ratio"]

    # 检查文件存在
    if not os.path.exists(first_path):
        log(f"  ❌ 首帧不存在: {first_path}")
        return False
    if not os.path.exists(last_path):
        log(f"  ❌ 尾帧不存在: {last_path}")
        return False

    # 检查是否已生成
    ep_dir = os.path.join(OUTPUT_DIR, episode_name)
    os.makedirs(ep_dir, exist_ok=True)
    out_video = os.path.join(ep_dir, f"{shot_info['shot']}.mp4")
    if os.path.exists(out_video) and os.path.getsize(out_video) > 100000:
        log(f"  ⏭️ 已存在，跳过")
        return True

    log(f"  📤 上传首帧: {os.path.basename(first_path)}")
    first_url = upload_image(first_path)
    if not first_url:
        return False

    log(f"  📤 上传尾帧: {os.path.basename(last_path)}")
    last_url = upload_image(last_path)
    if not last_url:
        return False

    log(f"  🎬 提交生成: {ratio} 720P")
    result = submit_video(shot_info["prompt"], first_url, last_url, ratio)
    log(f"  提交结果: {json.dumps(result, ensure_ascii=False)[:200]}")

    # 轮询等待完成
    log(f"  ⏳ 等待生成...")
    for i in range(120):  # 最长等待10分钟
        time.sleep(5)
        tasks = poll_tasks()
        if isinstance(tasks, list):
            for t in tasks:
                status = t.get("status", "")
                task_id = t.get("id") or t.get("taskId", "")
                progress = t.get("progress", 0)
                if status == "completed":
                    video_url = t.get("videoUrl")
                    if video_url:
                        log(f"  ✅ 生成完成！下载中...")
                        if download_video(task_id, out_video):
                            sz = os.path.getsize(out_video)
                            log(f"  💾 已保存: {out_video} ({sz//1024//1024}MB)")
                            return True
                elif status == "failed":
                    log(f"  ❌ 生成失败: {t.get('error', 'unknown')}")
                    return False
                elif status in ("running", "queued"):
                    if i % 6 == 0:
                        log(f"  ⏳ {status}... 进度 {progress}%")
        elif isinstance(tasks, dict):
            task_list = tasks.get("data") or tasks.get("tasks") or []
            for t in task_list:
                status = t.get("status", "")
                if status == "completed":
                    task_id = t.get("id") or t.get("taskId", "")
                    if download_video(task_id, out_video):
                        log(f"  💾 已保存: {out_video}")
                        return True
                elif status == "failed":
                    log(f"  ❌ 生成失败")
                    return False

    log(f"  ⚠️ 超时")
    return False

def main():
    log("=" * 60)
    log("🎬 高攀不起 - 全自动视频生成")
    log("=" * 60)

    # 1. 健康检查
    if not check_health():
        sys.exit(1)

    # 2. J卡登录
    login()

    # 3. 拉账号包
    purchase_session_pack()

    # 4. 遍历所有集数和镜头
    total = sum(len(ep["shots"]) for ep in EPISODES)
    done = 0
    failed = []

    for ep in EPISODES:
        ep_name = ep["episode"]
        log(f"\n{'='*40}")
        log(f"📋 开始处理: {ep_name} ({len(ep['shots'])} 镜头)")
        log(f"{'='*40}")

        for shot in ep["shots"]:
            log(f"\n▶ {ep_name} {shot['shot']} ({shot['ratio']})")
            success = process_shot(ep_name, shot)
            if success:
                done += 1
            else:
                failed.append(f"{ep_name} {shot['shot']}")
            log(f"  进度: {done}/{total}")
            time.sleep(3)  # 间隔避免过快提交

    # 5. 汇总
    log(f"\n{'='*60}")
    log(f"🎬 全部完成！成功 {done}/{total}")
    if failed:
        log("❌ 失败列表:")
        for f in failed:
            log(f"  - {f}")
    log(f"📁 视频保存在: {os.path.abspath(OUTPUT_DIR)}")
    log("=" * 60)

if __name__ == "__main__":
    main()
