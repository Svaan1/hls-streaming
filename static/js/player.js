const video = document.getElementById('hls-video');
const hlsUrl = '/hls/index.m3u8';

let isPowered = true;

function loadVideo() {
    const hls = new Hls();
    hls.loadSource(hlsUrl);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, function () {
        video.play();
    });
}

video.addEventListener('ended', () => {
    setTimeout(() => {
        console.log('Restarting video after 5 seconds...');
    }, 5000);
    loadVideo();
});

if (Hls.isSupported()) {
    loadVideo();
}

function toggleMute() {
    if (!isPowered) return;
    const video = document.getElementById('hls-video');
    video.muted = !video.muted;
    document.querySelector('.mute-indicator').classList.toggle('active', !video.muted);
}

function togglePower() {
    const video = document.getElementById('hls-video');
    isPowered = !isPowered;
    
    if (isPowered) {
        video.style.opacity = '1';
    } else {
        video.style.opacity = '0';
        video.muted = true;
        document.querySelector('.mute-indicator').classList.remove('active');
    }
    document.querySelector('.power-indicator').classList.toggle('active', isPowered);
}

function toggleFullscreen() {
    if (!isPowered) return;
    
    const screen = document.querySelector('.screen');
    screen.classList.toggle('fullscreen');
    const video = document.getElementById('hls-video');
    video.style.objectFit = screen.classList.contains('fullscreen') ? 'contain' : 'cover';
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const screen = document.querySelector('.screen');
        if (screen.classList.contains('fullscreen')) {
            screen.classList.remove('fullscreen');
            document.getElementById('hls-video').style.objectFit = 'cover';
        }
    }
});

document.querySelector('.power-indicator').classList.toggle('active', isPowered);
document.getElementById('hls-video').style.opacity = '1';