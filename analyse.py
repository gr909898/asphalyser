import io
import matplotlib
matplotlib.use('Agg')
import cv2 as cv
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt



def process_img(asph_path, thresh_cal = 200):
    asph = np.fromfile(asph_path, dtype = np.uint8)
    asph = cv.imdecode(asph, cv.IMREAD_GRAYSCALE)
    asph = cv.resize(asph, (800, 600), cv.INTER_AREA)

    asph_blur = cv.GaussianBlur(asph, (65, 65), 0)
    asph_bg = cv.divide(asph, asph_blur, scale=255)

    asph_fin = cv.medianBlur(asph_bg, 3)
    thresh_value = thresh_cal
    _, mask = cv.threshold(asph_fin, thresh_value, 255, cv.THRESH_BINARY_INV)

    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    mask_clean = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask_final = cv.morphologyEx(mask_clean, cv.MORPH_CLOSE, kernel)


    sizes = [2, 4, 8, 16, 32, 64, 128, 256]
    counts = []
    h, w = mask_final.shape

    text_lines = ["Подсчет ячеек..."]
    for s in sizes:
        count = 0
        for y in range(0, h, s):
            for x in range(0, w, s):
                block = mask_final[y:y+s, x:x+s]
                
                if np.any(block == 255):
                    count += 1
        counts.append(count)
        text_lines.append(f"Размер сетки: {s:3} | Занято ячеек: {count}")


    log_sizes = np.log10(sizes)
    log_counts = np.log10(counts)

    slope, intercept, r_value, p_value, std_err = linregress(log_sizes, log_counts)

    D = -slope
    R2 = r_value**2 

    text_lines.append("\n" + "="*40)
    text_lines.append(f"РЕЗУЛЬТАТ:")
    text_lines.append(f"Фрактальная размерность (D) = {D:.3f}")
    text_lines.append(f"Достоверность (R²) = {R2:.3f}")
    text_lines.append("="*40)


    fig = plt.figure(figsize=(8, 6))
    plt.plot(log_sizes, log_counts, 'bo', markersize=8, label='Экспериментальные данные')
    plt.plot(log_sizes, slope * log_sizes + intercept, 'r-', linewidth=2, label=f'Аппроксимация (наклон = -{D:.2f})')

    plt.title('Определение фрактальной размерности трещины\n(метод Box-Counting)', fontsize=14)
    plt.xlabel('Логарифм обратного размера ячейки  log(1/ε)', fontsize=12)
    plt.ylabel('Логарифм количества занятых ячеек  log(N)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    plot_img = cv.imdecode(np.frombuffer(buf.getvalue(), dtype=np.uint8), cv.IMREAD_COLOR)


    mask_bgr = cv.cvtColor(mask_final, cv.COLOR_GRAY2BGR)
    _, mask_buf = cv.imencode('.png', mask_bgr)

    return mask_buf.tobytes(), buf.getvalue(), "\n".join(text_lines), D, R2
