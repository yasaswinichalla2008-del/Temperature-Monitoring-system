#include "main.h"
#include <stdio.h>
#include <string.h>

#define GREEN_MAX_CENTI  3000U          /* <= 30.00 C green, > 30.00 C yellow */

#define YELLOW_PORT  GPIOB
#define YELLOW_PIN   GPIO_PIN_5         /* D4 */
#define GREEN_PORT   GPIOB
#define GREEN_PIN    GPIO_PIN_4         /* D5 */
#define LD2_PORT     GPIOA
#define LD2_PIN      GPIO_PIN_5         /* onboard LED, mirrors "yellow" */

ADC_HandleTypeDef hadc1;
UART_HandleTypeDef huart2;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_USART2_UART_Init(void);
static uint32_t ADC_ReadAveraged(uint8_t samples);

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_USART2_UART_Init();

    char message[64];

    /* Startup test: yellow 1 s, green 1 s, LD2 1 s */
    HAL_GPIO_WritePin(YELLOW_PORT, YELLOW_PIN, GPIO_PIN_SET);
    HAL_Delay(1000);
    HAL_GPIO_WritePin(YELLOW_PORT, YELLOW_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GREEN_PORT, GREEN_PIN, GPIO_PIN_SET);
    HAL_Delay(1000);
    HAL_GPIO_WritePin(GREEN_PORT, GREEN_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LD2_PORT, LD2_PIN, GPIO_PIN_SET);
    HAL_Delay(1000);
    HAL_GPIO_WritePin(LD2_PORT, LD2_PIN, GPIO_PIN_RESET);

    while (1)
    {
        uint32_t adcValue  = ADC_ReadAveraged(8);
        uint32_t tempCenti = (adcValue * 33000U + 2047U) / 4095U;

        if (tempCenti <= GREEN_MAX_CENTI)
        {
            HAL_GPIO_WritePin(GREEN_PORT,  GREEN_PIN,  GPIO_PIN_SET);
            HAL_GPIO_WritePin(YELLOW_PORT, YELLOW_PIN, GPIO_PIN_RESET);
            HAL_GPIO_WritePin(LD2_PORT,    LD2_PIN,    GPIO_PIN_RESET);
        }
        else
        {
            HAL_GPIO_WritePin(GREEN_PORT,  GREEN_PIN,  GPIO_PIN_RESET);
            HAL_GPIO_WritePin(YELLOW_PORT, YELLOW_PIN, GPIO_PIN_SET);
            HAL_GPIO_WritePin(LD2_PORT,    LD2_PIN,    GPIO_PIN_SET);
        }

        int len = snprintf(message, sizeof(message),
                           "ADC=%lu Temp=%lu.%02lu C\r\n",
                           (unsigned long)adcValue,
                           (unsigned long)(tempCenti / 100U),
                           (unsigned long)(tempCenti % 100U));
        HAL_UART_Transmit(&huart2, (uint8_t *)message, (uint16_t)len, HAL_MAX_DELAY);

        HAL_Delay(1000);
    }
}

static uint32_t ADC_ReadAveraged(uint8_t samples)
{
    uint32_t sum = 0;
    uint8_t good = 0;

    for (uint8_t i = 0; i < samples; i++)
    {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 100) == HAL_OK)
        {
            sum += HAL_ADC_GetValue(&hadc1);
            good++;
        }
        HAL_ADC_Stop(&hadc1);
    }
    return (good > 0) ? (sum / good) : 0;
}

void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);

    RCC_OscInitStruct.OscillatorType      = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState            = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState        = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource       = RCC_PLLSOURCE_HSI;
    RCC_OscInitStruct.PLL.PLLM            = 16;
    RCC_OscInitStruct.PLL.PLLN            = 336;
    RCC_OscInitStruct.PLL.PLLP            = RCC_PLLP_DIV4;
    RCC_OscInitStruct.PLL.PLLQ            = 7;
    RCC_OscInitStruct.PLL.PLLR            = 2;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
        Error_Handler();

    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                  RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
        Error_Handler();
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef g = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LD2_PORT, LD2_PIN, GPIO_PIN_RESET);

    g.Mode  = GPIO_MODE_OUTPUT_PP;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;

    g.Pin = GPIO_PIN_4 | GPIO_PIN_5;
    HAL_GPIO_Init(GPIOB, &g);

    g.Pin = LD2_PIN;
    HAL_GPIO_Init(LD2_PORT, &g);
}

static void MX_ADC1_Init(void)
{
    ADC_ChannelConfTypeDef sConfig = {0};

    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler        = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution            = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode          = DISABLE;
    hadc1.Init.ContinuousConvMode    = DISABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge  = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc1.Init.ExternalTrigConv      = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign             = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion       = 1;
    hadc1.Init.DMAContinuousRequests = DISABLE;
    hadc1.Init.EOCSelection          = ADC_EOC_SINGLE_CONV;
    if (HAL_ADC_Init(&hadc1) != HAL_OK)
        Error_Handler();

    sConfig.Channel      = ADC_CHANNEL_1;
    sConfig.Rank         = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_84CYCLES;
    if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
        Error_Handler();
}

static void MX_USART2_UART_Init(void)
{
    huart2.Instance          = USART2;
    huart2.Init.BaudRate     = 115200;
    huart2.Init.WordLength   = UART_WORDLENGTH_8B;
    huart2.Init.StopBits     = UART_STOPBITS_1;
    huart2.Init.Parity       = UART_PARITY_NONE;
    huart2.Init.Mode         = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl    = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    if (HAL_UART_Init(&huart2) != HAL_OK)
        Error_Handler();
}

void Error_Handler(void)
{
    __disable_irq();
    while (1) { }
}
