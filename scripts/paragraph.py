from pydantic import BaseModel
import tyro


class Paragraph(BaseModel, frozen=True):
    """
    This is the topics sentence, which summarizes what this class does.\\n

    This is the second paragraph, which goes on and on and on and on and on
    and on and on and on and on and on and on and on and on and on and on
    and on.

    This is the third paragraph, which is shorter.

    And the last one!
    """

    s: str = 'hello'


print(tyro.cli(Paragraph))
