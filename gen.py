import os
import json
import re

def natural_sort_key(s):
    """Sorts strings containing numbers naturally (e.g., 2.jpg comes before 10.jpg)"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def generate_html():
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    data = {}
    
    # Scan the current directory
    for item in os.listdir('.'):
        if os.path.isdir(item) and item != '__pycache__':
            images = []
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_extensions:
                    images.append(file)
            
            if images:
                images.sort(key=natural_sort_key)
                data[item] = images

    json_data = json.dumps(data, indent=4)

    # HTML/CSS/JS Template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>Notebook Viewer</title>
    <style>
        :root {{ --bg-dark: #1e1e1e; --bg-panel: #252526; --accent: #007acc; --text: #cccccc; }}
        body {{ margin: 0; display: flex; font-family: 'Segoe UI', Tahoma, sans-serif; height: 100vh; background: var(--bg-dark); color: var(--text); overflow: hidden; }}
        
        /* Sidebar Styles */
        #sidebar {{ width: 300px; min-width: 300px; background: var(--bg-panel); border-right: 1px solid #333; display: flex; flex-direction: column; z-index: 1000; transition: transform 0.3s ease; }}
        .sidebar-header {{ padding: 15px 20px; font-size: 18px; font-weight: bold; background: #333337; color: #fff; display: flex; justify-content: space-between; align-items: center; }}
        #close-sidebar {{ display: none; background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; }}
        #folderList {{ overflow-y: auto; flex-grow: 1; }}
        .folder-btn {{ display: block; width: 100%; padding: 15px 20px; background: transparent; color: #ccc; border: none; border-bottom: 1px solid #333; cursor: pointer; text-align: left; font-size: 15px; transition: background 0.2s; }}
        .folder-btn:hover {{ background: #2a2d2e; }}
        .folder-btn.active {{ background: #37373d; color: #fff; border-left: 4px solid var(--accent); padding-left: 16px; font-weight: bold; }}
        
        /* Main UI Styles */
        #main {{ flex-grow: 1; display: flex; flex-direction: column; width: 100%; position: relative; }}
        #header {{ padding: 10px 15px; background: var(--bg-panel); border-bottom: 1px solid #333; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; }}
        
        .header-left {{ display: flex; align-items: center; gap: 15px; }}
        #menu-btn {{ display: none; background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; padding: 0 5px; }}
        #folderTitle {{ margin: 0; font-size: 18px; font-weight: 500; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }}
        
        /* Toolbar (Zoom & Nav) */
        .toolbar {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
        .btn-group {{ display: flex; background: #333; border-radius: 6px; overflow: hidden; }}
        button.tool-btn {{ padding: 8px 15px; font-size: 14px; cursor: pointer; background: transparent; color: white; border: none; border-right: 1px solid #444; font-weight: bold; }}
        button.tool-btn:last-child {{ border-right: none; }}
        button.tool-btn:hover:not(:disabled) {{ background: #444; }}
        button.tool-btn.primary {{ background: var(--accent); }}
        button.tool-btn.primary:hover:not(:disabled) {{ background: #0098ff; }}
        button.tool-btn:disabled {{ color: #777; cursor: not-allowed; }}
        #counter {{ font-size: 15px; color: #bbb; min-width: 70px; text-align: center; }}
        
        /* Image Viewer Area */
        #viewer-container {{ flex-grow: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; background: #0b0b0b; position: relative; }}
        #viewer {{ max-width: 100%; height: auto; object-fit: contain; transform-origin: top center; transition: width 0.2s ease; cursor: pointer; }}
        .fit-screen {{ max-height: 100%; width: auto !important; }}
        
        #overlay {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 999; }}
        .hidden {{ display: none !important; }}

        /* Mobile Responsiveness */
        @media (max-width: 800px) {{
            #sidebar {{ position: fixed; top: 0; left: 0; height: 100%; transform: translateX(-100%); }}
            #sidebar.open {{ transform: translateX(0); }}
            #close-sidebar {{ display: block; }}
            #menu-btn {{ display: block; }}
            #overlay.active {{ display: block; }}
            #folderTitle {{ font-size: 16px; max-width: 150px; }}
            .nav-text {{ display: none; }} /* Hide 'Prev'/'Next' text on mobile, keep arrows */
        }}
    </style>
</head>
<body>
    <div id="overlay"></div>
    
    <div id="sidebar">
        <div class="sidebar-header">
            Notebooks
            <button id="close-sidebar">&times;</button>
        </div>
        <div id="folderList"></div>
    </div>
    
    <div id="main">
        <div id="header">
            <div class="header-left">
                <button id="menu-btn">&#9776;</button>
                <h2 id="folderTitle">Select a notebook...</h2>
            </div>
            
            <div class="toolbar hidden" id="controls">
                <div class="btn-group">
                    <button class="tool-btn" id="btnZoomOut" title="Zoom Out">-</button>
                    <button class="tool-btn" id="btnZoomReset" title="Fit to Screen">Fit</button>
                    <button class="tool-btn" id="btnZoomIn" title="Zoom In">+</button>
                </div>
                <div class="btn-group">
                    <button id="btnPrev" class="tool-btn primary">&#9664; <span class="nav-text">Prev</span></button>
                    <span id="counter" class="tool-btn" style="cursor:default;"></span>
                    <button id="btnNext" class="tool-btn primary"><span class="nav-text">Next</span> &#9654;</button>
                </div>
            </div>
        </div>
        
        <div id="viewer-container">
            <img id="viewer" src="" class="hidden fit-screen" />
        </div>
    </div>
    
    <script>
        const data = {json_data};
        
        let currentFolder = null;
        let currentIndex = 0;
        let currentZoom = 0; // 0 means 'fit-screen'
        
        // DOM Elements
        const DOM = {{
            folderList: document.getElementById('folderList'),
            viewer: document.getElementById('viewer'),
            viewerContainer: document.getElementById('viewer-container'),
            folderTitle: document.getElementById('folderTitle'),
            controls: document.getElementById('controls'),
            btnPrev: document.getElementById('btnPrev'),
            btnNext: document.getElementById('btnNext'),
            counter: document.getElementById('counter'),
            sidebar: document.getElementById('sidebar'),
            overlay: document.getElementById('overlay'),
            btnMenu: document.getElementById('menu-btn'),
            btnCloseSidebar: document.getElementById('close-sidebar'),
            btnZoomIn: document.getElementById('btnZoomIn'),
            btnZoomOut: document.getElementById('btnZoomOut'),
            btnZoomReset: document.getElementById('btnZoomReset')
        }};

        // 1. Initialize Sidebar
        for (const folder in data) {{
            const btn = document.createElement('button');
            btn.className = 'folder-btn';
            btn.textContent = folder;
            btn.onclick = () => loadFolder(folder);
            DOM.folderList.appendChild(btn);
        }}

        // 2. Folder & Image Loading
        function loadFolder(folder) {{
            currentFolder = folder;
            currentIndex = 0;
            DOM.folderTitle.textContent = folder;
            DOM.viewer.classList.remove('hidden');
            DOM.controls.classList.remove('hidden');

            // Highlight active
            document.querySelectorAll('.folder-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('.folder-btn')).find(b => b.textContent === folder);
            if(activeBtn) activeBtn.classList.add('active');

            closeSidebar();
            resetZoom();
            showImage();
        }}

        function showImage() {{
            const images = data[currentFolder];
            const path = encodeURIComponent(currentFolder) + '/' + encodeURIComponent(images[currentIndex]);
            DOM.viewer.src = path;
            
            DOM.counter.textContent = (currentIndex + 1) + ' / ' + images.length;
            DOM.btnPrev.disabled = currentIndex === 0;
            DOM.btnNext.disabled = currentIndex === images.length - 1;
            
            DOM.viewerContainer.scrollTop = 0; // scroll to top of new page
            preloadNext();
        }}

        function preloadNext() {{
            const images = data[currentFolder];
            if (currentIndex < images.length - 1) {{
                const img = new Image();
                img.src = encodeURIComponent(currentFolder) + '/' + encodeURIComponent(images[currentIndex + 1]);
            }}
        }}

        // 3. Navigation Functions
        const goPrev = () => {{ if (currentIndex > 0) {{ currentIndex--; showImage(); }} }};
        const goNext = () => {{ if (currentIndex < data[currentFolder].length - 1) {{ currentIndex++; showImage(); }} }};

        DOM.btnPrev.onclick = goPrev;
        DOM.btnNext.onclick = goNext;

        // Smart image clicking (Left side = Prev, Right side = Next)
        DOM.viewer.onclick = (e) => {{
            const rect = DOM.viewer.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            if (clickX < rect.width * 0.35) goPrev(); // Clicked left 35%
            else goNext(); // Clicked right 65%
        }};

        // Double click to toggle zoom
        DOM.viewer.ondblclick = (e) => {{
            e.stopPropagation();
            if (currentZoom === 0) setZoom(100);
            else resetZoom();
        }};

        // 4. Zoom Logic
        function setZoom(percentage) {{
            currentZoom = Math.max(20, Math.min(percentage, 300)); // Clamp between 20% and 300%
            DOM.viewer.classList.remove('fit-screen');
            DOM.viewer.style.width = currentZoom + '%';
        }}
        function resetZoom() {{
            currentZoom = 0;
            DOM.viewer.style.width = '';
            DOM.viewer.classList.add('fit-screen');
        }}

        DOM.btnZoomIn.onclick = () => setZoom(currentZoom === 0 ? 120 : currentZoom + 20);
        DOM.btnZoomOut.onclick = () => setZoom(currentZoom === 0 ? 80 : currentZoom - 20);
        DOM.btnZoomReset.onclick = resetZoom;

        // 5. Mobile Sidebar Toggles
        const openSidebar = () => {{ DOM.sidebar.classList.add('open'); DOM.overlay.classList.add('active'); }};
        const closeSidebar = () => {{ DOM.sidebar.classList.remove('open'); DOM.overlay.classList.remove('active'); }};
        
        DOM.btnMenu.onclick = openSidebar;
        DOM.btnCloseSidebar.onclick = closeSidebar;
        DOM.overlay.onclick = closeSidebar;

        // 6. Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (!currentFolder) return;
            if (e.key === 'ArrowLeft') goPrev();
            if (e.key === 'ArrowRight') goNext();
            if (e.key === '+' || e.key === '=') DOM.btnZoomIn.click();
            if (e.key === '-') DOM.btnZoomOut.click();
            if (e.key === '0') resetZoom();
        }});
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print("Success! A beautiful, mobile-friendly index.html has been generated.")

if __name__ == "__main__":
    generate_html()