const video = document.getElementById('hls-video');
const channels = window.availableChannels;
let currentChannelIndex = parseInt(localStorage.getItem('currentChannelIndex')) || 0;
let volumeBeforeMute = 0;
let currentVolume = 0;
let isPowered = true;
let volumeTimeout;
video.volume = currentVolume;

document.querySelector('.power-btn').classList.toggle('active', isPowered);
document.getElementById('hls-video').style.opacity = '1';

// Events

if (Hls.isSupported() && channels.length > 0) {
    const channelName = channels[currentChannelIndex];
    const url = _getHlsUrl(channelName);
    _loadVideo(url);
}

video.addEventListener('ended', () => {
    setTimeout(() => {
        console.log('Restarting video after 5 seconds...');
    }, 5000);

    let channel = channels[currentChannelIndex];
    let url = _getHlsUrl(channel);
    _loadVideo(url);
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const screen = document.querySelector('.screen');
        if (screen.classList.contains('fullscreen')) {
            screen.classList.remove('fullscreen');
            document.getElementById('hls-video').style.objectFit = 'cover';
        }
    }
});

// Functions

function _getHlsUrl(channelName) {
    return `/hls/${channelName}/index.m3u8`;
}

function _loadVideo(channelUrl) {
    if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(channelUrl);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {
            video.play();
        });
    }
}

function _updateVolumeIndicator() {
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

function _switchChannel(index) {
    if (!isPowered) return;
    currentChannelIndex = index;
    localStorage.setItem('currentChannelIndex', currentChannelIndex);
    const channelName = channels[currentChannelIndex];
    const url = _getHlsUrl(channelName);
    _loadVideo(url);
}

// Button Handlers

function toggleFullscreen() {
    if (!isPowered) return;
    const screen = document.querySelector('.screen');
    screen.classList.toggle('fullscreen');
    const video = document.getElementById('hls-video');
    video.style.objectFit = screen.classList.contains('fullscreen') ? 'contain' : 'cover';
}

function previousChannel() {
    if (channels.length <= 1) return;
    currentChannelIndex = (currentChannelIndex - 1 + channels.length) % channels.length;
    _switchChannel(currentChannelIndex);
}

function nextChannel() {
    if (channels.length <= 1) return;
    currentChannelIndex = (currentChannelIndex + 1) % channels.length;
    _switchChannel(currentChannelIndex);
}

function decreaseVolume() {
    if (!isPowered) return;
    currentVolume = Math.max(0, currentVolume - 0.1);
    video.volume = currentVolume;
    
    console.log(video.muted, currentVolume);
    if (!video.muted && currentVolume < 0.01) {
        video.muted = true;
        document.querySelector('.mute-btn').classList.toggle('active', !video.muted);
    }
    _updateVolumeIndicator();
}

function increaseVolume() {
    if (!isPowered) return;
    currentVolume = Math.min(1.0, currentVolume + 0.1);
    video.volume = currentVolume;
    
    if (video.muted) {
        video.muted = false;
        document.querySelector('.mute-btn').classList.toggle('active', !video.muted);
    }
    _updateVolumeIndicator();
}

function toggleMute() {
    if (!isPowered) return;
    video.muted = !video.muted;
    if (video.muted) {
        volumeBeforeMute = currentVolume;
        currentVolume = 0;
    } else {
        currentVolume = volumeBeforeMute || 0.5;
    }
    video.volume = currentVolume;
    document.querySelector('.mute-btn').classList.toggle('active', !video.muted);
    _updateVolumeIndicator();
}

function togglePower() {
    const video = document.getElementById('hls-video');
    isPowered = !isPowered;
    
    if (isPowered) {
        video.style.opacity = '1';
        video.volume = currentVolume;
    } else {
        video.style.opacity = '0';
        video.muted = true;
        document.querySelector('.mute-btn').classList.remove('active');
    }
    document.querySelector('.power-btn').classList.toggle('active', isPowered);
}
