# HLS Streaming

I always liked the feeling of waking up in the middle of the night, turning the tv on, and being surprised by what was playing at the time, so much so that the silence and cozy feeling stuck with me to this day.

Maybe thats just nostalgia, but i wanted to replicate a little bit of this feeling, so i created an application to randomly and constantly convert videos to the hls format aiming to replicate a stream-like functionality.

## How it works

1. FastAPI serves the root html and starts the streaming manager background task.

2. The background task constantly chooses the "playlist" and converts it using `ffmpeg` following [hls standards](https://en.wikipedia.org/wiki/HTTP_Live_Streaming), while taking care of cleaning any temporary files and watching over the state of the `ffmpeg` process.

3. The files generated by the `ffmpeg` process are generated inside a FastAPI mounted directory, so they are available via HTTP.

4. The index html takes care of consuming the stream, using a hls specific player to request for the video index and its segments, restarting the process when the current video is over.

## To-do

- ~~Style the html~~ ✅
- ~~dynamic configuration of the conversion process, such as quality and latency related flags~~ ✅
- ~~more thorough exception handling in the loop and start streaming functions~~ ✅
- ~~better ffmpeg process logging~~ ✅
- ~~Multiple channels (multiple instances of the streaming manager, one for each playlist, change config lib to dynaconf to use a toml file instead of a .env), computational expensive but kinda cool~~ ✅
- Prometheus for resource tracking (figure out the ffmpeg having multiple pids thing)
- grafana for resource utilization monitoring
- docker config for resource limiting nitpicks, such as thread and memory reserving
- Add metadata (title, author, whatever i can get from the video metadata) from the current video and channel
- Add volume control to the player
- typing
- Add some documenting
- real-time chats
- user upload on videos
- figure out process dying suddenly (linux)
- comments in the middle of the video (lol)
- tts

## How to run

    1. Download and install `uv`
    2. Run the make default command

## Challenges

- Creating a ffmpeg process for every video is redundant and fail prone, but creating a single stream of multiple files also has its challenges

- At the current time, i still did not figure out how to avoid audio desync when trying to use ffmpeg's concat demuxer, maybe its just a config thing, maybe its not feasible, we'll see

- My guess is the size of the segments between each file are too different

- Cannot run on reload mode due to the event loop being implemented differently, so you cannot run processes with it
