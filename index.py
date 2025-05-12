from flask import Flask, request, jsonify
import yt_dlp
import http.cookiejar
from waitress import serve



video_format_ids = [
    137,  # 1080p (best video quality)
    136,  # 720p (HD)
    135,  # 480p (SD)
    134,  # 360p
    133,  # 240p
    160,  # 144p
    22,   # 720p (MP4, commonly used)
    18,   # 360p (MP4, commonly used)
    278,  # 1440p (2K)
    266,  # 4K (best video quality)
]


audio_format_ids = [
    "140",  # 128 kbps (AAC)
    "141",  # 256 kbps (AAC)
    "251",  # 160 kbps (WebM audio)
    "250",  # 192 kbps (WebM audio)
    "249",  # 128 kbps (WebM audio)
    "171",  # 192 kbps (AAC)
    "160",  # 128 kbps (MP3 audio)
    "139",  # 96 kbps (MP3 audio)
]


app = Flask(__name__)

@app.route('/get_streaming_url', methods=['GET'])
def get_streaming_url():
    video_url = request.args.get('url')
    cookie_file = request.args.get('cookies.txt', default=None)  # Allow cookie file to be passed

    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    try:
        # Create yt-dlp options
        ydl_opts = {
            'format': 'bestaudio+bestaudio',  # Try to get the best video and audio combination
            'quiet': True,                    # Suppress output
            'noplaylist': True,               # Don't process playlists
            'extractaudio': True,             # Extract audio
            'audioquality': 1,                # Highest quality audio
            'forceurl': True,  
            'cookiefile': "cookies.txt"           # Force use of URLs instead of m3u8
        }

        # If a cookie file is provided, load the cookies
        # if cookie_file:
        #     cookie_jar = http.cookiejar.MozillaCookieJar(cookie_file)
        #     cookie_jar.load(cookie_file, ignore_discard=True, ignore_expires=True)
        #     ydl_opts['cookiefile'] = cookie_file  # Use the cookie file with yt-dlp
        
        # Fetch the video information using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)

            # Check if we have audio and video formats
            video_url = None
            audio_url = None
            newList=[]
            
            for items in info_dict['formats']:
                 if items['format_id'] in audio_format_ids:
            #    if audio_format_ids.index(newList['format_id']) > -1:
                  newList.append({"url":items['url']})
             
           
            return newList
            
            # Extract the video URL
            if 'formats' in info_dict:
                for format in info_dict['formats']:
                    if format.get('vcodec') != 'none' and 'url' in format:
                        video_url = format['url']
                        break

            # Extract the audio URL if available
            if 'formats' in info_dict:
                for format in info_dict['formats']:
                    if format.get('acodec') != 'none' and 'url' in format:
                        audio_url = format['url']
                        break

            return jsonify({
                'video_url': video_url if video_url else 'Video URL not available',
                'audio_url': audio_url if audio_url else 'Audio URL not available'
            })

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
#     app.run(debug=False)
     serve(app, host='0.0.0.0', port=5000)