from django.core.paginator import Paginator

class PageNav:

    NUM_PAGES = 50
    NAV_SIZE = 11
    NAV_LEFT_PART_LMT = 5
    NAV_RIGHT_PART_LMT = 5
    OBJS_ON_PAGE = 30

    def __init__(self, current_page_num, paginator_page=None, url_template='',
                 qs=None, objs_on_page=None):

        if objs_on_page and objs_on_page > 0: PageNav.OBJS_ON_PAGE = objs_on_page

        if qs:
            self.paginator = Paginator(qs, PageNav.OBJS_ON_PAGE)
            self.paginator_page = self.paginator.page(current_page_num)
        elif paginator_page:
            self.paginator_page = paginator_page
            self.paginator = self.paginator_page.paginator
        else:
            self.paginator_page = None
            self.paginator = None
        if self.paginator:
            PageNav.NUM_PAGES = self.paginator.num_pages
        else:
            PageNav.NUM_PAGES = 0
        self.url_template = url_template
        # if self.paginator_page: PageNav.NUM_PAGES = self.paginator_page.paginator.num_pages
        self.current_page_num = current_page_num
        self.first_page = None
        self.last_page = None
        self.toleft10 = None
        self.toleft100 = None
        self.toright10 = None
        self.toright100 = None
        self.nav_pages = []
        # print(PageNav.OBJS_ON_PAGE, PageNav.NUM_PAGES, self.paginator.count)
        self.nav_pages_init()

    def go_next(self):
        if self.current_page_num < PageNav.NUM_PAGES: self.current_page_num += 1
        return self.current_page_num

    def __next__(self):
        if self.paginator_page.has_next():
            return {'pagenum': self.current_page_num + 1,
                    'pageurl': self.url_template.format(page=self.current_page_num + 1)}
        return None

    def go_previous(self):
        if self.current_page_num > 1: self.current_page_num -= 1
        return self.current_page_num

    def previous(self):
        if self.paginator_page.has_previous():
            return {'pagenum': self.current_page_num - 1,
                    'pageurl': self.url_template.format(page=self.current_page_num - 1)}
        return None

    @staticmethod
    def reverse_arr(arr):
        ln = len(arr)
        half_ln = round(ln / 2)
        for i in range(half_ln):
            tmp = arr[ln - 1 - i]
            arr[ln - 1 - i] = arr[i]
            arr[i] = tmp
        return None

    def nav_pages_init(self):
        self._nav_pages = []

        if not self.paginator:
            return

        if self.current_page_num <= PageNav.NAV_LEFT_PART_LMT + 1: start_num = 1
        else: start_num = self.current_page_num - PageNav.NAV_LEFT_PART_LMT

        left_suppl = PageNav.NAV_LEFT_PART_LMT - (self.current_page_num - start_num)

        if PageNav.NUM_PAGES - self.current_page_num <= PageNav.NAV_RIGHT_PART_LMT: end_num = PageNav.NUM_PAGES
        else: end_num = self.current_page_num + PageNav.NAV_RIGHT_PART_LMT

        right_suppl = PageNav.NAV_RIGHT_PART_LMT - (end_num - self.current_page_num)

        for p in range(start_num, end_num + 1):
            self._nav_pages.append(p)

        for i in list(range(1, left_suppl + 1)):
            if start_num - i > 0:
                self._nav_pages.insert(0, start_num - i)
                left_suppl -= 1
        for i in list(range(1,left_suppl + 1)):
            if end_num + i <= PageNav.NUM_PAGES:
                self._nav_pages.append(end_num + i)
                right_suppl -= 1
                left_suppl -= 1

        for i in list(range(1, right_suppl + 1)):
            if end_num + i <= PageNav.NUM_PAGES:
                self._nav_pages.append(end_num + i)
                right_suppl -= 1
        for i in list(range(1, right_suppl + 1)):
            if start_num - i > 0:
                self._nav_pages.insert(0, start_num - i)
                left_suppl -= 1
                right_suppl -= 1

        for pnum in self._nav_pages:
            self.nav_pages.append({'pagenum': pnum, 'pageurl': self.url_template.format(page=pnum)})

        if self.current_page_num > 1:
            self.first_page = {'pagenum': 1, 'pageurl': self.url_template.format(page=1)}
        if self.current_page_num < self.paginator_page.paginator.num_pages:
            self.last_page = {'pagenum': self.paginator_page.paginator.num_pages,
                              'pageurl': self.url_template.format(page=self.paginator_page.paginator.num_pages)}
        if self.current_page_num - 10 > 0:
            pg = self.current_page_num - 10
            self.toleft10 = {'pagenum': pg, 'pageurl': self.url_template.format(page=pg)}
        if self.current_page_num - 100 > 0:
            pg = self.current_page_num - 100
            self.toleft100 = {'pagenum': pg, 'pageurl': self.url_template.format(page=pg)}
        if self.current_page_num + 10 <= self.paginator_page.paginator.num_pages:
            pg = self.current_page_num + 10
            self.toright10 = {'pagenum': pg, 'pageurl': self.url_template.format(page=pg)}
        if self.current_page_num + 100 <= self.paginator_page.paginator.num_pages:
            pg = self.current_page_num + 100
            self.toright100 = {'pagenum': pg, 'pageurl': self.url_template.format(page=pg)}

        return None


# if __name__ == '__main__':
#     # l = [1,2,3,4,5,6,7, 8]
#     # PageNav.reverse_arr(l)
#     # print(l)
#     ranges = list(range(1,11)) + list(range(51, 61)) + list(range(91,101))
#     for p in ranges:
#         pn = PageNav(p )
#         print (pn.nav_pages, 'current=', p)
