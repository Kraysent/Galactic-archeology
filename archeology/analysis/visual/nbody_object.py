class NbodyObject:
    def __init__(self,
        color: str = 'r',
        name: str = '',
        whole_part: slice = slice(0, None)
    ) -> None:
        self.color = color
        self.name = name
        self.whole_part = whole_part