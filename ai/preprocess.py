# def preprocess_image(image_path: str, save_path: str):
#     import cv2
#     import numpy as np

#     img = cv2.imread(image_path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#     enhanced = clahe.apply(gray)
#     kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
#     sharpened = cv2.filter2D(enhanced, -1, kernel)
#     result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
#     cv2.imwrite(save_path, result)


def preprocess_image(image_path: str, save_path: str):
    import cv2
    import numpy as np

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Увеличиваем контраст с помощью CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Смягчение изображения вместо сильной резкости
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Перевод обратно в 3-канальный формат
    result = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(save_path, result)