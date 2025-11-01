from flask import Flask, request, jsonify
import yt_dlp
import http.cookiejar
from waitress import serve
import time

progressive_format_ids = [
    "18",  # 360p
    "22",  # 720p
    "59",  # 480p
    "37",  # 1080p
    "17",  # 144p
    "36"   # 240p
]


video_format_ids = [
    "137",  # 1080p (best video quality)
    "136",  # 720p (HD)
    "135",  # 480p (SD)
    "134",  # 360p
    "133",  # 240p
    "160",  # 144p
    "22,"   # 720p (MP4, commonly used)
    "18,"   # 360p (MP4, commonly used)
    "278",  # 1440p (2K)
    "266",  # 4K (best video quality)
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

def getVideo_authorInfo(yt_dlp_res):
     return {
        #  "video_info":{
        #  "title":yt_dlp['title'],
        #  "comment_count":yt_dlp['comment_count'],
        #  "description":yt_dlp['description'],
        #  "duration":yt_dlp['duration'],
        #  "filesize":yt_dlp['filesize'],
        #  "availability":yt_dlp['availability'],
        #  "webpage_url":yt_dlp['webpage_url'],
        #  "view_count":yt_dlp['view_count'],
        #  "was_live":yt_dlp['was_live'],
        #  "url":yt_dlp['url'],
        #  "upload_date":yt_dlp['upload_date'],
        #  "thumbnail":yt_dlp['thumbnail'],
        #  }, 
        #  "author_info":{
        #       "channel":yt_dlp_res['title'],
            #   "channel_follower_count":yt_dlp_res['channel_follower_count'],
            #   "channel_is_verified":yt_dlp_res['channel_is_verified'],
            #   "channel_url":yt_dlp_res['channel_url'],
        #  }
     }

def init_ytdlp(video_url):
        ydl_opts = {
            'format': 'bestvideo+bestaudio',  # Try to get the best video and audio combination
            'quiet': True,                    # Suppress output
            'noplaylist': True,  
            'skip_download': True,
            'forceurl': True, 
            'cookiefile': 'cookies.txt'
           # Force use of URLs instead of m3u8
        }

        # If a cookie file is provided, load the cookies
        # if cookie_file:
        #     cookie_jar = http.cookiejar.MozillaCookieJar(cookie_file)
        #     cookie_jar.load(cookie_file, ignore_discard=True, ignore_expires=True)
        #     ydl_opts['cookiefile'] = cookie_file  # Use the cookie file with yt-dlp
        
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
        return info_dict


def to_netscape(cookie_list):
    lines = ["# Netscape HTTP Cookie File"]
    for cookie in cookie_list:
        domain = cookie["domain"]
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = cookie.get("path", "/")
        secure = "TRUE" if cookie.get("isSecure") else "FALSE"
        expires = str(int(cookie["expiresDate"] / 1000)) if cookie.get("expiresDate") else "0"
        name = cookie["name"]
        value = cookie["value"]
        line = f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
        lines.append(line)
    return "\n".join(lines)

@app.route('/streaming_url/audio', methods=['POST'])
def get_audio_streaming_url():

    starting= time.time()

    video_url = request.args.get('url')
    cookies = request.get_json().get('cookies')
    netscape= to_netscape(cookies)
    if cookies:
          with open('cookies.txt', 'w') as f:
              f.write(str(netscape))
          

    # cookie_file = request.args.get('cookies.txt', default=None)  # Allow cookie file to be passed

    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    try:
        # Create yt-dlp options
            res = init_ytdlp(video_url)
            pre_format_code=0
            streaming_url=''
            resolution=''
            for items in res['formats']:
                 format_id= items['format_id']
                 if format_id in audio_format_ids:
                      int_format_id= int(format_id)
                    #   if int_format_id==234:
                    #        pre_format_code=int_format_id
                    #        streaming_url=items['url']
                    #        resolution= items['format_note']
                    #        break
                      if pre_format_code < int_format_id:
                           pre_format_code=int_format_id
                           streaming_url=items['url']
                           resolution= items['format_note']
                  #if audio_format_ids.index(newList['format_id']) > -1:
                #   newList.append({"url":items['url']})
             
            
            
            return jsonify({
                 "resonse_took":time.time() - starting, 
                 "format_type":"bestaudio", 
                 "format_note":resolution, 
                 "format_id":pre_format_code, 
                 "streaming_url":streaming_url})
            

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    


@app.route('/streaming_url/video', methods=['POST'])
def get_video_streaming_url():
    starting= time.time()

    video_url = request.args.get('url')
    # cookie_file = request.args.get('cookies.txt', default=None)  # Allow cookie file to be passed

    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    try:
        # Create yt-dlp options
            res = init_ytdlp(video_url)
            pre_format_code=0
            resolution=''
            streaming_url=''
            return jesonify(res)
            for items in res['formats']:
                 format_id= items['format_id']
                 if format_id in progressive_format_ids:
                      int_format_id= int(format_id)
                    #1080p
                      if int_format_id ==  37:
                           pre_format_code=int_format_id
                           streaming_url= items['url']
                           resolution= items['format_note']
                           break
                      elif int_format_id == 22 : # 720p
                           pre_format_code=int_format_id
                           streaming_url= items['url']
                           resolution= items['format_note']
                           break
                      elif int_format_id == 59: #480p
                           pre_format_code=int_format_id
                           streaming_url= items['url']
                           resolution= items['format_note']
                           break
                      
                      elif int_format_id == 18: #360p
                           pre_format_code=int_format_id
                           streaming_url= items['url']
                           resolution= items['format_note']
                           break
                      
                    #   elif pre_format_code < int_format_id:
                    #        pre_format_code=int_format_id
                    #        streaming_url= items['url']
                    #        resolution= items['format_note']
                # if audio_format_ids.index(newList['format_id']) > -1:
                #   newList.append({"url":items['url']})
        
    
          
            return jsonify({
                 "resonse_took":time.time() - starting, 
                 "format_type":"bestvideo", 
                 "format_note":resolution, 
                 "format_id":pre_format_code, 
                 "streaming_url":streaming_url
            })
            

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    #  app.run(debug=False)
     serve(app, host='0.0.0.0', port=5000)
