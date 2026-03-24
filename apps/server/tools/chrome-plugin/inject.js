// inject.js
const iframe = document.createElement('iframe');
iframe.src = "https://finai-bda97.web.app";
iframe.style.position = "fixed";
iframe.style.bottom = "10px";
iframe.style.right = "10px";
iframe.style.width = "400px";
iframe.style.height = "600px";
iframe.style.zIndex = "99999";
iframe.style.border = "1px solid #ccc";
document.body.appendChild(iframe);
