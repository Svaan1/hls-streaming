const video = document.getElementById('hls-video');
let currentChannelIndex = 0;
const channels = window.availableChannels;

function getHlsUrl(channelName) {
    return `/hls/${channelName}/index.m3u8`;
}

function loadVideo(channelUrl) {
    if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(channelUrl);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {
            video.play();
        });
    }
}

function switchChannel(index) {
    if (!isPowered) return;
    currentChannelIndex = index;
    const channelName = channels[currentChannelIndex];
    loadVideo(getHlsUrl(channelName));
}

function nextChannel() {
    if (channels.length <= 1) return;
    currentChannelIndex = (currentChannelIndex + 1) % channels.length;
    switchChannel(currentChannelIndex);
}

function previousChannel() {
    if (channels.length <= 1) return;
    currentChannelIndex = (currentChannelIndex - 1 + channels.length) % channels.length;
    switchChannel(currentChannelIndex);
}

// Initialize with first channel
if (Hls.isSupported() && channels.length > 0) {
    loadVideo(getHlsUrl(channels[0]));
}

let isPowered = true;

video.addEventListener('ended', () => {
    setTimeout(() => {
        console.log('Restarting video after 5 seconds...');
    }, 5000);
    loadVideo(getHlsUrl(channels[currentChannelIndex]));
});

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