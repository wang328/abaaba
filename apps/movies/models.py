from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel
from tinymce.models import HTMLField


# Create your models here.


class MoviesType(BaseModel):
    """   定义视频的模型类  """
    name = models.CharField(max_length=20, verbose_name="类别名称")  # 填写视频的类型  电影、电视剧、动漫、沙雕视频等类型
    logo = models.CharField(max_length=20, verbose_name="标识")  # 填写类型标识  movies tv animation shadiao等标识

    class Meta:
        db_table = 'df_movies_type'
        verbose_name = "电影类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Movies(BaseModel):
    """   定义视频SPU模型类   """
    name = models.CharField(max_length=20, verbose_name="电影SPU名称")
    # 富文本类型：带有格式的文本类型
    detail = HTMLField(blank=True, verbose_name="视频类型描述")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "df_movies"
        verbose_name = "电影SPU"
        verbose_name_plural = verbose_name


class MoviesSKU(BaseModel):
    """  电影SKU模型类  """
    status_choices = (
        (0, "会员"),
        (1, "非会员")
    )
    type = models.ForeignKey("MoviesType", verbose_name="电音类型")
    movies = models.ForeignKey("movies", verbose_name="商品SPU")
    name = models.CharField(max_length=30, verbose_name="视频名称")
    desc = models.CharField(max_length=256, verbose_name="视频简介")
    cover_image = models.ImageField(upload_to="movies", verbose_name="视频封面")
    movie_file = models.FileField(upload_to="videos", verbose_name="视频")
    count = models.IntegerField(default=0, verbose_name="播放量")
    status = models.SmallIntegerField(default=0, choices=status_choices, verbose_name="视频状态")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "df_movies_sku"
        verbose_name = "电影"
        verbose_name_plural = verbose_name
