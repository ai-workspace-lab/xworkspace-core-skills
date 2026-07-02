# Reconstruction Rules

## Text

1. Use exact user-provided text when available.
2. If extracting text from image, verify visually. Do not hallucinate unreadable characters.
3. Chinese default fonts: Microsoft YaHei, SimHei, Source Han Sans SC, Noto Sans CJK SC.
4. Avoid distorted text boxes. Do not apply horizontal scale unless explicitly necessary.
5. Preserve line breaks when they affect visual hierarchy.

## Colors

1. Use sampled colors from the source image when possible.
2. Use a limited palette for reconstructed shapes.
3. Prefer matching perceived color over exact noisy pixel values.

## Shapes

1. Rectangular cards and bands should be editable.
2. Rounded corners must use realistic radius; avoid exaggerated rounded cards unless present in source.
3. Thin separator lines should not become too thick in PPT.

## Icons and logos

1. Keep logos as cropped assets unless the logo is trivially geometric.
2. For icons, choose: editable only if simple; crop if complex.
3. Do not create fake logo text.

## Charts

1. Simple bar charts can be reconstructed as editable rectangles and labels.
2. Dense academic charts should be cropped as an asset.
3. If user needs editability, rebuild chart separately with approximate data and flag approximation.

## Visual fallback

When visual fidelity is critical, place a full-slide fallback image/SVG at the back and overlay editable elements. This helps demonstration and protects against obvious mismatch.
