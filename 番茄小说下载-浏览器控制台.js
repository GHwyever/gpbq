// 在浏览器控制台(F12)中运行的下载代码
// 使用方法：
// 1. 打开 https://fanqienovel.com/page/7546956076533419070
// 2. 完成滑动验证码（如果需要）
// 3. 按F12打开开发者工具，切换到Console
// 4. 复制粘贴以下全部代码，按回车执行
// 5. 等待下载完成

(async function() {
    const BOOK_ID = location.pathname.split('/')[2];
    const BOOK_NAME = document.querySelector('h1')?.innerText || '攀龙';

    console.log(`开始下载《${BOOK_NAME}》...`);

    // 获取章节列表
    async function getChapters() {
        const resp = await fetch(`https://fanqienovel.com/page/${BOOK_ID}`);
        const html = await resp.text();
        const doc = new DOMParser().parseFromString(html, 'text/html');

        const chapters = [];
        doc.querySelectorAll('.chapter-item a, .chapter a').forEach(a => {
            const href = a.getAttribute('href');
            const title = a.innerText.trim();
            if (href && title) {
                chapters.push({
                    id: href.split('/').pop(),
                    title: title
                });
            }
        });
        return chapters;
    }

    // 获取单章内容
    async function getContent(chapterId) {
        const resp = await fetch(`https://fanqienovel.com/reader/${chapterId}`);
        const html = await resp.text();
        const doc = new DOMParser().parseFromString(html, 'text/html');

        let content = '';
        const contentDiv = doc.querySelector('.muye-reader-content');
        if (contentDiv) {
            contentDiv.querySelectorAll('p').forEach(p => {
                content += p.innerText + '\n';
            });
        }
        return content;
    }

    // 下载文件
    function download(filename, text) {
        const blob = new Blob([text], {type: 'text/plain;charset=utf-8'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // 主流程
    const chapters = await getChapters();
    console.log(`共找到 ${chapters.length} 章`);

    let fullText = `《${BOOK_NAME}》\n${'='.repeat(50)}\n\n`;
    let success = 0;
    let fail = 0;

    for (let i = 0; i < chapters.length; i++) {
        const ch = chapters[i];
        console.log(`[${i+1}/${chapters.length}] 下载: ${ch.title}`);

        const content = await getContent(ch.id);
        if (content && content.length > 50) {
            fullText += `\n${ch.title}\n${'-'.repeat(30)}\n${content}\n`;
            success++;
        } else {
            console.log(`  ✗ ${ch.title} 内容为空`);
            fail++;
        }

        // 延迟500ms
        await new Promise(r => setTimeout(r, 500));
    }

    download(`${BOOK_NAME}.txt`, fullText);
    console.log(`\n✅ 下载完成! 成功: ${success}, 失败: ${fail}`);
    console.log(`文件已保存: ${BOOK_NAME}.txt`);
})();
