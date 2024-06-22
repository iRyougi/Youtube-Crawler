import googleapiclient.discovery
import googleapiclient.errors

def get_authenticated_service():
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "YOUR_API_KEY"  # 将 'YOUR_API_KEY' 替换为您的 YouTube API 密钥
    
    return googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

def get_videos(youtube, start_date, end_date):
    videos = []
    next_page_token = None
    while True:
        request = youtube.search().list(
            part="snippet",
            publishedAfter=start_date,
            publishedBefore=end_date,
            type="video",
            order="viewCount",
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response["items"]:
            video_id = item["id"]["videoId"]
            video_info = youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()
            if "items" in video_info and video_info["items"]:
                statistics = video_info["items"][0]["statistics"]
                if "viewCount" in statistics:
                    view_count = int(statistics["viewCount"])
                    if view_count > 1000:
                        videos.append({
                            "videoId": video_id,
                            "title": item["snippet"]["title"],
                            "link": f"https://www.youtube.com/watch?v={video_id}",
                            "viewCount": view_count
                        })
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return videos

def get_comments(youtube, video_id):
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": comment["textDisplay"],
                "likeCount": comment["likeCount"]
            })
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403 and 'commentsDisabled' in e.content.decode():
            print(f"视频 {video_id} 的评论已禁用，跳过该视频。")
        else:
            raise e
    return comments

def main(start_date, end_date, output_file):
    youtube = get_authenticated_service()
    videos = get_videos(youtube, start_date, end_date)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for video in videos:
            video_id = video["videoId"]
            comments = get_comments(youtube, video_id)
            sorted_comments = sorted(comments, key=lambda x: x["likeCount"], reverse=True)
            
            f.write(f"视频标题: {video['title']}\n")
            f.write(f"链接: {video['link']}\n")
            f.write(f"播放量: {video['viewCount']}\n")
            f.write("评论:\n")
            for comment in sorted_comments:
                f.write(f"点赞数: {comment['likeCount']}\n评论: {comment['text']}\n\n")
            f.write("\n\n")

if __name__ == "__main__":
    # 用户输入开始和结束日期
    start_date = "2023-06-01T00:00:00Z"
    end_date = "2024-06-10T23:59:59Z"
    output_file = "youtube_comments.txt"
    main(start_date, end_date, output_file)