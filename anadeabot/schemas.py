from typing import Optional

from langchain_core.pydantic_v1 import BaseModel, Field

from anadeabot import options


class DesignChoice(BaseModel):
    """A set of user T-shirt attribute design choices."""

    color: Optional[options.TShirtColor | str] = Field(
        default=None,
        description="""
            If a user intents or chooses a specific T-shirt COLOR or to change
            their previous choice of COLOR. The color is the main color of a
            fabric a T-shirt is made of, that is the background color, not
            taking into account color of decorations. If a user chooses some
            CUSTOM color, not explicitly listed here, then extract it as a
            string instead."""
    )

    size: Optional[options.TShirtSize] = Field(
        default=None,
        description="""
            If a user intents or chooses a specific T-shirt SIZE or to change their
            previous choice of SIZE. The size of a T-shirt determines whether a
            person will fit into the clothing or whether it is too small or too
            large for a particular person. For example, children need smaller sizes
            like XS or S, but adults need sizes such as M, L. For people with big
            bodies a T-shirt of size XL or XLL may be necessary. If a user's
            specified size DOES NOT MATCH any of the available sizes, LEAVE IT EMPTY."""
    )

    style: Optional[options.TShirtStyle] = Field(
        default=None,
        description="""
            If a user intents or chooses a specific T-shirt STYLE or to change their
            previous choice of STYLE. The style of a T-shirt determines whether it 
            has sleeves or not, or which fabric it is made of, and whether it is
            appropriate for female or male body. If a user's specified style DOES
            NOT MATCH any of the available styles, LEAVE IT EMPTY."""
    )

    gender: Optional[options.TShirtGender] = Field(
        default=None,
        description="""
            If a user intents or chooses a specific T-shirt GENDER or to change
            their previous choice of GENDER. The gender means whether the T-shirt
            is suitable for a man or a woman or similar in this manner. Whether a
            T-shirt is suitable for a specific gender can depend on its color,
            size, style, or a picture on the clothing."""
    )

    printing: Optional[options.TShirtPrintingOptions] = Field(
        default=None,
        description="""
            If a user intents or chooses a specific T-shirt PRINTING OPTIONS or to
            change their previous choice of PRINTING OPTIONS. A printing option or
            a method of printing is the method of putting a picture onto a fabric.
            It determines the material the image is made of or quality of an image.
            Embroidery for example produces very stylish pictures made of special
            threads, and direct-to-garment printing sprays ink on the fabric."""
    )


class BooleanOutput(BaseModel):
    """Respond in a binary manner, like yes or no, true or false."""

    value: bool = Field(..., description='True or False')


class UserIntent(BaseModel):
    """Determine the most probable intent of a user. If you can select any of them,
     leave all empty. DO NOT FORCE YOURSELF TO MAKE A CHOICE."""

    preference: bool = Field(
        default=None,
        description="""This is an intent of a human when a human wants to make a
                    design decision or choose a specific property of a T-shirt.
                    If a user expressed an intent to choose an option of some
                    T-shirt property, fire this flag.""")

    decision: bool = Field(
        default=None,
        description="""If a user has design options selected and if we previously
                    asked a human to confirm their order, and they approve that
                    they indeed ready to make an order of the T-shirt or the do
                    not want to proceed with the order, that design is correct
                    and they are ready to make an order or cancel an order of a
                    T-shirt, fire this flag.""")

    question: bool = Field(
        default=None,
        description="""Given the above conversation, if a HUMAN, not a system or AI,
                    asks a question, for example, about our offerings, available
                    T-shirt attribute design options, or other features of our platform,
                    fire this flag.""")

    struggle: bool = Field(
        default=None,
        description="""Given the above conversation, determine whether a user
                    has faced some obstacle, or is struggling trying to accomplish
                    some goal. You can take into account user's tone, expressions,
                    number of repetitions of a question, or this sort of behaviour.""")

    help: bool = Field(
        default=None,
        description="""Given the above conversation, if we previously suggested
                    a user to make a request to customer support, and now the
                    user agreed to send a request for help from support,
                    then fire this flag.""")

    request: bool = Field(
        default=None,
        description="""Given the above conversation, if we did not ask a user about
                    contacting support, but a user expressed desire to make a request
                    to support, to tell them something, or to ask a question.""")

    agent: bool = Field(
        default=None,
        description="""In any other case, where a user just want to talk, in a free
                    conversation."""
    )


class ExpectedIntent(BaseModel):
    struggle: int = 0
    help: int = 0
    choice: int = 0
    decision: int = 0
    question: int = 0


class SupportRequest(BaseModel):
    """A user wants to make a request to customer support because they faced
    some problem, have a question or require a help of a human specialist."""

    details: str = Field(
        default=None,
        description="""A concise, self-contained summary of user's support
                    request extracted from the conversation with a user."""
    )
