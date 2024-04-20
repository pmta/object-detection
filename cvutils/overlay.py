from PIL import Image, ImageDraw, ImageFont


def roundedTextbox(
    img,
    box,
    text,
    font=ImageFont.truetype("arial.ttf", 20),
    text_offset_x=20,
    text_offset_y=20,
    vspace=2,
    hspace=2,
    font_scale=1.0,
    background_RGBA=(128, 128, 128, 172),
    text_RGBA=(255, 255, 255, 225),
    thickness=2,
    alpha=0.6,
    gamma=1,
):
    """

    ##########################################################
    #       | hspace                                         #
    #       |                                                #
    # ----- *     *   ******  *       *          ***         #
    #  v    *     *   *       *       *        *     *       #
    #  s    *******   ***     *       *        *     *       #
    #  p    *     *   *       *       *        *     *       #
    #  a    *     *   ******  ******  ******     ***         #
    #  c                                                     #
    #  e    ^------------- textWidth ----------------^       #
    ##########################################################     ^  text_offset_x
                                                               \   '
                                                                \  '
                                                                 \ '
                                              text_offset_y       \'
                                                            <..... +----------------------
                                                                   | (box_x1, box_y1)
                                                                   |
                                                                   |
                                                                   |
                                                                   |
    """
    im = img.convert(mode="RGBA")
    fnt = font

    textWidth = fnt.getlength(text)
    textHeight = fnt.size

    # Create overlay image, same size as original image
    overlay = Image.new("RGBA", im.size, (255, 255, 255, 0))

    # "Draw" on overlay image
    _d = ImageDraw.Draw(overlay)

    _d.rectangle(box, outline=text_RGBA)
    box_x1, box_y1, box_x2, box_y2 = box

    ### Textbox area
    # Bind textBox tepleft corner always at least at zero (0,0) (topleft of image)
    textbox_topLeft_x = max(0, box_x1 - text_offset_x - textWidth - vspace * 2)
    textbox_topLeft_y = max(0, box_y1 - text_offset_y - textHeight - hspace * 2)

    # print(text_offset_x)
    # print(textWidth)
    # calculate all other coords based on the textbox top left to propagate the binding
    # textbox_botRight = (max(0, box_x1 - text_offset_x), max(0, box_y1 - text_offset_y))
    textbox_botRight_x = textbox_topLeft_x + textWidth + vspace * 2
    textbox_botRight_y = textbox_topLeft_y + textHeight + hspace * 2

    _d.rounded_rectangle(
        xy=[
            (textbox_topLeft_x, textbox_topLeft_y),
            (textbox_botRight_x, textbox_botRight_y),
        ],
        radius=5,
        fill=background_RGBA,
        outline=text_RGBA,
        width=thickness,
    )

    # Screen text
    text_topLeft_x = textbox_topLeft_x + vspace
    # text_topLeft_y = textbox_topLeft_y + hspace
    text_topLeft_y = textbox_topLeft_y

    _d.text((text_topLeft_x, text_topLeft_y), text, font=fnt, fill=text_RGBA)

    # Connector
    connector_topLeft_x = textbox_botRight_x
    connector_topLeft_y = textbox_botRight_y

    if textbox_botRight_x > box_x1 and textbox_botRight_y < box_y1:
        # textbox goes past the detection box topleft corner but does not overlap in Y direction
        # Move connector to start from left bottom of the textbox
        connector_topLeft_x = textbox_topLeft_x
        # connector_topLeft_y remains the same

    if textbox_topLeft_x < box_x1 and textbox_botRight_y < box_y1:
        # Only draw the connector when textbox is not overlapping with the detection box
        _d.line(
            ((connector_topLeft_x, connector_topLeft_y), (box_x1, box_y1)),
            fill=(198, 198, 198),
            width=thickness,
        )

    # Composite overlay on original image
    out = Image.alpha_composite(im, overlay)
    return out
