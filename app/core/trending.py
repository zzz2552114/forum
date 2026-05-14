import asyncio
from datetime import UTC, datetime, timedelta
from loguru import logger

# 基础重力系数，数值越大，帖子热度随时间衰减越快
GRAVITY = 1.5

def calculate_hot_score(
    created_at: datetime,
    like_count: int,
    comment_count: int,
    bookmark_count: int = 0
) -> float:
    """
    计算帖子的热度分数 (基于 Hacker News 算法的改良版)
    
    公式: Score = P / (T + 2)^G
    P: 互动得分 (点赞=1分, 收藏=2分, 评论=3分)
    T: 帖子发布至今经历的小时数
    G: 重力常数 GRAVITY
    """
    # 1. 计算互动总得分 (权重可根据业务调整)
    points = (like_count * 1.0) + (bookmark_count * 2.0) + (comment_count * 3.0)
    
    # 2. 计算帖子发布至今的小时数
    now = datetime.now(UTC).replace(tzinfo=None)
    age_delta = now - created_at
    age_in_hours = max(age_delta.total_seconds() / 3600.0, 0.0)
    
    # 3. 核心衰减公式
    score = points / ((age_in_hours + 2.0) ** GRAVITY)
    
    # 保留 4 位小数
    return round(score, 4)

def update_post_hot_score(post) -> float:
    """
    传入一个 Post 实例对象，利用它的数据重新计算并更新 hot_score。
    注：这里只赋值，不执行数据库的 save()，把保存操作留给调用方，方便事务控制或合并更新。
    """
    new_score = calculate_hot_score(
        created_at=post.created_at,
        like_count=post.like_count,
        comment_count=post.comment_count,
        bookmark_count=getattr(post, "bookmark_count", 0),
    )
    post.hot_score = new_score
    return new_score

async def sync_all_hot_scores_task():
    """
    后台守护任务：每隔 10 分钟重新计算一次近期活跃帖子的热度分数。
    因为即便没有互动，帖子分数也会随时间衰减，必须定时刷新以保证老帖下沉。
    """
    from app.models.forum import Post
    from app.models.enums import ContentStatus
    
    while True:
        try:
            logger.info("Starting periodic hot_score sync...")
            
            # 只计算最近 7 天的帖子，太老的帖子默认已经沉底，节省算力
            # 兼容上面改为无时区 tzinfo=None 的写法
            seven_days_ago = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=7)
            
            # 取出所有 7 天内发布的有效帖子
            posts = await Post.filter(
                status=ContentStatus.PUBLISHED, 
                created_at__gte=seven_days_ago
            ).all()
            
            update_count = 0
            for post in posts:
                update_post_hot_score(post)
                await post.save(update_fields=["hot_score"])
                update_count += 1
                
            logger.info(f"Successfully synced hot_score for {update_count} posts.")
        except Exception as e:
            logger.error(f"Error syncing hot_score: {e}")
            
        # 休息 10 分钟
        await asyncio.sleep(600)
