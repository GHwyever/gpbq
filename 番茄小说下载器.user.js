// ==UserScript==
// @name         番茄小说简化下载器
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  简化版番茄小说下载脚本
// @author       Assistant
// @match        *://fanqienovel.com/page/*
// @match        *://fanqienovel.com/reader/*
// @grant        GM_download
// @grant        GM_xmlhttpRequest
// @grant        unsafeWindow
// ==/UserScript==

(function() {
    'use strict';

    // 等待页面加载完成
    window.addEventListener('load', function() {
        initDownloader();
    });

    function initDownloader() {
        // 创建下载按钮
        const btn = document.createElement('button');
        btn.innerText = '📥 下载本书';
        btn.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 99999;
            padding: 10px 20px;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        `;

        btn.onclick = function() {
            const bookId = location.pathname.split('/')[2];
            if (!bookId) {
                alert('无法获取书籍ID');
                return;
            }
            downloadBook(bookId);
        };

        document.body.appendChild(btn);
        console.log('番茄小说下载器已加载');
    }

    async function downloadBook(bookId) {
        console.log('开始下载书籍:', bookId);

        // 获取章节列表
        const chapters = await getChapterList(bookId);
        if (!chapters || chapters.length === 0) {
            alert('获取章节列表失败');
            return;
        }

        console.log('找到章节数:', chapters.length);
        let content = '';

        for (let i = 0; i < chapters.length; i++) {
            const ch = chapters[i];
            console.log(`下载第${i+1}/${chapters.length}章: ${ch.title}`);

            const chapterContent = await getChapterContent(ch.id);
            if (chapterContent) {
                content += `\n${ch.title}\n${'='.repeat(30)}\n${chapterContent}\n`;
            }

            // 延迟避免请求过快
            await sleep(500);
        }

        // 下载文件
        const bookName = document.querySelector('h1')?.innerText || '未知书名';
        downloadFile(`${bookName}.txt`, content);
        alert('下载完成！');
    }

    async function getChapterList(bookId) {
        try {
            const resp = await fetch(`https://fanqienovel.com/page/${bookId}`);
            const html = await resp.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const chapters = [];
            const links = doc.querySelectorAll('.chapter-item a, .chapter a');

            links.forEach(a => {
                const href = a.getAttribute('href');
                const title = a.innerText.trim();
                if (href && title) {
                    const id = href.split('/').pop();
                    chapters.push({ id, title });
                }
            });

            return chapters;
        } catch (e) {
            console.error('获取章节列表失败:', e);
            return [];
        }
    }

    async function getChapterContent(chapterId) {
        try {
            const resp = await fetch(`https://fanqienovel.com/reader/${chapterId}`);
            const html = await resp.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // 尝试多种方式获取内容
            let content = '';
            const contentDiv = doc.querySelector('.muye-reader-content');

            if (contentDiv) {
                const paragraphs = contentDiv.querySelectorAll('p');
                paragraphs.forEach(p => {
                    content += p.innerText + '\n';
                });
            }

            return content;
        } catch (e) {
            console.error('获取章节内容失败:', e);
            return '';
        }
    }

    function downloadFile(filename, content) {
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
})();
