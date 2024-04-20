import math
import cv2
from PIL import Image, ImageDraw, ImageFont


def imageOverlay(
    img,
    boxes,
    classNames,
    confidenceThreshold=0.7,
    font=ImageFont.truetype("arial.ttf", 20),
    text_offset_x=20,
    text_offset_y=20,
    vspace=2,
    hspace=2,
    background_RGBA=(128, 128, 128, 172),
    text_RGBA=(255, 255, 255, 225),
    thickness=2,
    scale_x=1.0,
    scale_y=1.0,
):
    # Scaling resulting image is rather costly

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
    vspace = vspace + thickness
    hspace = hspace + thickness
    im = img.convert(mode="RGBA")
    fnt = font

    # Create overlay image, same size as original image
    overlay = Image.new("RGBA", im.size, (255, 255, 255, 0))

    # "Draw" on overlay image
    _d = ImageDraw.Draw(overlay)

    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[
            0
        ]  # box xy,xy coordinates (easier to input to opencv) just get first detected box
        box_x1, box_y1, box_x2, box_y2 = int(x1), int(y1), int(x2), int(y2)

        # Top left + width and height
        # bbox = int(x1), int(y1), int(x2 - x1), int(y2 - y1)

        ## Confidence
        conf = (
            math.ceil((box.conf[0]) * 100) / 100
        )  # confidentce with 2 decimal accuracy

        if conf > confidenceThreshold:
            # Class name
            cls = box.cls[0]
            if int(cls) < len(classNames):
                currentClass = classNames[int(cls)]
            else:
                currentClass = int(cls)

            textWidth = fnt.getlength(currentClass)
            textHeight = fnt.size

            _d.rectangle(
                [box_x1, box_y1, box_x2, box_y2], outline=text_RGBA, width=thickness
            )
            # box_x1, box_y1, box_x2, box_y2 = box

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
            text_topLeft_y = (
                textbox_topLeft_y + hspace - 2
            )  # text has more space above than below

            _d.text(
                (text_topLeft_x, text_topLeft_y), currentClass, font=fnt, fill=text_RGBA
            )

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
    if scale_x != 1.0 or scale_y != 1.0:
        _tImg = Image.alpha_composite(im, overlay)
        out = _tImg.resize(
            (int(_tImg.size[0] * scale_x), int(_tImg.size[1] * scale_y)),
            Image.Resampling.BILINEAR,
        )
    else:
        out = Image.alpha_composite(im, overlay)

    return out
