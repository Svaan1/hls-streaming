const video = document.getElementById('hls-video');
const channels = window.availableChannels;
let currentChannelIndex = 0;
let volumeTimeout;
let currentVolume = 0;
video.volume = currentVolume;

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
    video.muted = !video.muted;
    currentVolume = video.muted ? 0 : currentVolume;
    document.querySelector('.mute-btn').classList.toggle('active', !video.muted);
    if (!video.muted && currentVolume === 0) {
        currentVolume = 0.5;
        video.volume = currentVolume;
    }
    updateVolumeIndicator();
}

function increaseVolume() {
    if (!isPowered) return;
    currentVolume = Math.min(1.0, currentVolume + 0.1);
    video.volume = currentVolume;
    updateVolumeIndicator();
    if (video.muted) {
        video.muted = false;
        document.querySelector('.mute-btn').classList.add('active');
    }
}

function decreaseVolume() {
    if (!isPowered) return;
    currentVolume = Math.max(0, currentVolume - 0.1);
    video.volume = currentVolume;
    updateVolumeIndicator();
    
    if (currentVolume === 0) {
        video.muted = true;
        document.querySelector('.mute-btn').classList.remove('active');
    }
}

function togglePower() {
    const video = document.getElementById('hls-video');
    isPowered = !isPowered;
    
    if (isPowered) {
        video.style.opacity = '1';
        video.volume = currentVolume;  // Restore volume when turning on
    } else {
        video.style.opacity = '0';
        video.muted = true;
        document.querySelector('.mute-btn').classList.remove('active');
    }
    document.querySelector('.power-btn').classList.toggle('active', isPowered);
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

document.querySelector('.power-btn').classList.toggle('active', isPowered);
document.getElementById('hls-video').style.opacity = '1';

function updateVolumeIndicator() {
    const volumeIndicator = document.querySelector('.volume-indicator');
    const volumeLevel = document.querySelector('.volume-level');
    const volumeText = document.querySelector('.volume-text');
    const percentage = Math.round(currentVolume * 100);
    
    volumeLevel.style.width = `${percentage}%`;
    volumeText.textContent = `${percentage}%`;
    
    volumeIndicator.classList.add('show');
    
    clearTimeout(volumeTimeout);
    volumeTimeout = setTimeout(() => {
        volumeIndicator.classList.remove('show');
    }, 2000);
}