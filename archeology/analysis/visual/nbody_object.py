class NbodyObject:
    def __init__(self,
        color: str = 'r',
        label: str = '',
        whole_part: slice = slice(0, None)
    ) -> None:
        self.color = color
        self.label = label
        self.whole_part = whole_part