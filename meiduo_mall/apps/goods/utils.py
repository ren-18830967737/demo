

def get_breadcrumb(category):

    breadcrumb = {
        'cat1':'',
        'cat2':'',
        'cat3':'',
    }
    #一级分类
    if category.parent is None:
        breadcrumb['cat1']=category
    #二级分类
    elif category.subs.count()== 0:
        breadcrumb['cat3']=category
        breadcrumb['cat2']=category.parent
        breadcrumb['cat1']= category.parent.parent
    #三级分类
    else:
        breadcrumb['cat2']=category
        breadcrumb['cat1']=category.parent

    return breadcrumb