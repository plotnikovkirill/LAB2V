import matplotlib


try:
    matplotlib.use('TkAgg')
except:
    pass

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

#Привет от Власова Сергея и Плотникова Кирилла
def calculate_lab1(S_val, R_val, C_val, U_zi_val):
    """
    S_val: Крутизна транзистора (А/В)
    R_val: Нагрузочное сопротивление (Ом)
    C_val: Суммарная емкость узла (Ф)
    U_zi_val: Входное напряжение (В)
    """
    # Константы
    r_si = 10e3  # Внутреннее сопротивление транзистора
    U_p = 5.0  # Напряжение питания


    t_end = 150e-9
    N = 2000
    h = t_end / N
    t = np.linspace(0, t_end, N)

    # Массив для напряжения
    U_out = np.zeros(N)
    U_out[0] = U_p  # В начале конденсатор заряжен до 5В

    # Коэффициент K = 1 / C_total
    K = 1.0 / C_val

    # ЦИКЛ ЭЙЛЕРА
    for n in range(N - 1):
        # 1. Если напряжение упало до 0, останавливаем разряд
        if U_out[n] <= 0:
            U_out[n + 1] = 0
            continue

        # 2. Составляем уравнение токов
        # Ток от источника (через R): (Up - U) / R
        I_supply = (U_p - U_out[n]) / R_val

        # Ток утечки (через r_си): U / r_si
        I_leak = U_out[n] / r_si

        # Ток транзистора (активный режим): S * U_вх
        I_trans = S_val * U_zi_val

        # Сумма токов (втекающие минус вытекающие)
        # dU/dt = (1/C) * I_sum
        Current_sum = I_supply - I_leak - I_trans

        dU_dt = K * Current_sum

        # 3. Делаем шаг
        next_val = U_out[n] + h * dU_dt

        # 4. Проверка на "уход в минус"
        U_out[n + 1] = max(0, next_val)

    return t, U_out


# интерфейс

init_S = 0.3e-3
init_R = 1000  # 1 кОм
init_C = 50e-12  # 50 пФ
init_U = 5.0  # 5 В

# Создаем окно
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(left=0.1, bottom=0.35)  # Место снизу для ползунков

# Первичный расчет
t, u = calculate_lab1(init_S, init_R, init_C, init_U)

# Рисуем линию
line, = ax.plot(t * 1e9, u, lw=3, color='blue', label='Выходное напряжение $U_{C_н}$')

ax.set_title("Лаб 1: Инвертор (Интерактивная модель)")
ax.set_xlabel("Время, нс")
ax.set_ylabel("Напряжение, В")
ax.set_ylim(-0.2, 5.5)
ax.set_xlim(0, 150)
ax.grid(True)
ax.legend()
ax.axhline(0, color='black', linewidth=1)  # Ось X


# ползунки
axcolor = 'lightgoldenrodyellow'

# Слайдер Крутизны (S)
ax_S = plt.axes([0.15, 0.25, 0.65, 0.03], facecolor=axcolor)
s_S = Slider(ax_S, 'Крутизна S [мА/В]', 0.1, 5.0, valinit=init_S * 1000)

# Слайдер Сопротивления (R)
ax_R = plt.axes([0.15, 0.20, 0.65, 0.03], facecolor=axcolor)
s_R = Slider(ax_R, 'Нагрузка R [Ом]', 100, 5000, valinit=init_R)

# Слайдер Емкости (C)
ax_C = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor=axcolor)
s_C = Slider(ax_C, 'Емкость C [пФ]', 10, 200, valinit=init_C * 1e12)

# Слайдер Входа (U_in)
ax_U = plt.axes([0.15, 0.10, 0.65, 0.03], facecolor=axcolor)
s_U = Slider(ax_U, 'Вход U_зи [В]', 0.0, 5.0, valinit=init_U)


#update

def update(val):
    # Получаем новые данные
    S_new = s_S.val / 1000.0  # мА -> А
    R_new = s_R.val
    C_new = s_C.val * 1e-12  # пФ -> Ф
    U_new = s_U.val

    # Считаем заново
    t_new, u_new = calculate_lab1(S_new, R_new, C_new, U_new)

    # Обновляем график
    line.set_ydata(u_new)
    fig.canvas.draw_idle()


# Подключаем функцию update к слайдерам
s_S.on_changed(update)
s_R.on_changed(update)
s_C.on_changed(update)
s_U.on_changed(update)

# Кнопка сброса
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Сброс', color=axcolor, hovercolor='0.975')


def reset(event):
    s_S.reset()
    s_R.reset()
    s_C.reset()
    s_U.reset()


button.on_clicked(reset)

plt.show()