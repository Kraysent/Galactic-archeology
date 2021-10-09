class NbodyObject:
    def __init__(self,
        part: slice,
        color: str = 'r',
        label: str = '',
        whole_part: slice = slice(0, None)
    ) -> None:
        self.part = part
        self.color = color
        self.label = label
        self.whole_part = whole_part