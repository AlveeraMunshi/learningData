library(tidyverse)
data <- tibble(
  Product = c("020230 - Bovine, frozen", "030342 - Yellowfin tuna", "Autos - Stellantis"),
  US_Import_Value_USD = c(50000000, 10000000, 60000000),
  US_Applied_Tariff = c(0, 0, 0),
  Mexico_Export_Value_USD = c(40000000, 8000000, 60000000),
  Mexico_Applied_Tariff = c(0, 0, 2)
) %>%
  mutate(
    US_Tariff_Revenue = US_Import_Value_USD * (US_Applied_Tariff / 100),
    Mexico_Tariff_Revenue = Mexico_Export_Value_USD * (Mexico_Applied_Tariff / 100),
    Total_Trade = US_Import_Value_USD + Mexico_Export_Value_USD,
    US_Burden = US_Tariff_Revenue / Total_Trade * 100,
    Mexico_Burden = Mexico_Tariff_Revenue / Total_Trade * 100
  )
summary <- data %>% 
  summarise(Total_US = sum(US_Tariff_Revenue), Total_Mexico = sum(Mexico_Tariff_Revenue)) %>%
  pivot_longer(cols = c(Total_US, Total_Mexico), names_to = "Country", values_to = "Revenue") %>%
  mutate(Country = recode(Country, "Total_US" = "US", "Total_Mexico" = "Mexico"))
ggplot(data, aes(x = Product)) +
  geom_bar(aes(y = US_Burden, fill = "US"), stat = "identity") +
  geom_bar(aes(y = Mexico_Burden, fill = "Mexico"), stat = "identity", alpha = 0.7) +
  labs(title = "Estimated Tariff Burden: US vs Mexico (2022)", y = "Burden (% of Trade Value)") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_fill_manual(values = c("US" = "blue", "Mexico" = "red"))
ggsave("plot1.png")
ggplot(summary, aes(x = Country, y = Revenue, fill = Country)) +
  geom_bar(stat = "identity") +
  labs(title = "Estimated Tariff Revenue: US vs Mexico (2022)", y = "Revenue (USD)") +
  scale_fill_manual(values = c("US" = "blue", "Mexico" = "red"))
ggsave("plot2.png")