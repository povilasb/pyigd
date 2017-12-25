from aiomock import AIOMock


class AsyncMock(AIOMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.async_return_value = kwargs.get('async_return_value')
        self.async_side_effect = kwargs.get('async_side_effect')
