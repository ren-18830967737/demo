from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU
from apps.goods.utils import get_breadcrumb
from utils.response_code import RETCODE

#商品页面展示
class ListView(View):

    def get(self, request, category_id, page_num):

        #获取分类数据
        category = GoodsCategory.objects.get(id=category_id)
        #判断分类数据
        if category is None:
            return render(request, '404.html')
        #获取面包屑导航
        breadcrumb = get_breadcrumb(category)
        # 获取排序功能
        sort = request.GET.get('sort')
        #设置排序
        if sort == 'default':
            order_field = 'create_time'
        if sort == 'price':
            order_field = '-price'
        else:
            order_field = 'sales'


        #获取数据并分类
        skus = SKU.objects.filter(category=category).order_by(order_field)
        #设置分页

        from django.core.paginator import Paginator
        #创建实例对象
        page_data = Paginator(object_list=skus, per_page=5)
        #获取当前页数数据
        page_data_num = page_data.page(page_num)
        #总页数
        total_page = page_data.num_pages
        context = {

            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_data_num,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        # 返回响应
        return render(request, 'list.html', context=context)








#热销排行展示
class SalesView(View):

    def get(self,request,category_id):

        skus = SKU.objects.filter(category_id=category_id).order_by('-sales')[0:2]

        sku_list = []

        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        return JsonResponse({
            'code':RETCODE.OK,
            'errmsg':'OK',
            'hot_skus':sku_list
        })







#商品详情页面
class DetailView(View):

    def get(self,request,sku_id):

        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request,'detail.html',context)
