from django.shortcuts import render
from django.views import View
from django import http

from .models import Area
from meiduo_mall.utils.response_code import RETCODE


class AreaView(View):
    """省市区查询"""
    def get(self, request):
        # 1. 获取area_id查询参数
        area_id = request.GET.get('area_id')
        # 2. 判断是否有area_id 如果没有说明查询所有省数据
        if area_id is None:
            # 查询所有省数据
            province_qs = Area.objects.filter(parent=None)
            # 模型转字典: 序列化 输出
            province_list = []  # 包装所有省的字典结构数据
            for province in province_qs:
                province_list.append({
                    'id': province.id,
                    'name': province.name
                })
            # JsonResponse()  json.dumps
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})


        else:
            # 如果有area_id查询area_id指定的下级所有行政区
            try:
                # 查询指定area_id对应行政区
                parent_model = Area.objects.get(id=area_id)
                # 查询area_id对待行政区的下级所有行政区
                sub_qs = parent_model.subs.all()

            except Area.DoesNotExist:
                return http.HttpResponseForbidden('area_id不存在')

            # 将sub_qs查询中的模型转字典
            sub_list = []  # 包装所有下级行政区字典结构数据
            for sub in sub_qs:
                sub_list.append({
                    'id': sub.id,
                    'name': sub.name
                })

            # 包装行政区及下级行政区数据
            data_dict = {
                'id': parent_model.id,
                'name': parent_model.name,
                'subs': sub_list
            }

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': data_dict})


