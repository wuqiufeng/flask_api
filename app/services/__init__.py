

class Pagination(object):

    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def pages(self):
        return int(ceil(self.total / float(self.per_page)))

    @property
    def offset(self):
        return (self.page - 1) * self.per_page

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def dict(self):
        return {'page': self.page, 'pages': self.pages, 'per_page': self.per_page, 'total': self.total}

    @property
    def json(self):
        return json.dumps(self.dict)

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                    self.page - left_current - 1 < num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def __repr__(self):
        return '<Pagination: %d/%d,%d/%d>' % (self.page, self.pages, self.per_page, self.total)


class BaseService():
    def __init__(self, model=None, name='BaseService'):
        self.name = name
        self.model = model
        self.pager = Pagination

    def condition_parser(self, args, config, model=None):  # args表示get请求schemas里面的所有参数集
        for arg, expr in config.items():
            if arg in args:
                val = args[arg]
                if expr == "like":
                    yield getattr(model if model else self.model, arg).like(u"%{}%".format(val))
                elif expr == "eq":
                    yield getattr(model if model else self.model, arg) == val
                elif expr == "gt":
                    yield getattr(model if model else self.model, arg) > val
                elif expr == "ls":
                    yield getattr(model if model else self.model, arg) < val
                elif expr == "in":
                    yield getattr(model if model else self.model, arg).in_(val)
                else:
                    pass