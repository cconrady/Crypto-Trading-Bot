
if(!require(data.table)) {install.packages("data.table"); library(data.table)}
if(!require(formattable)) {install.packages("formattable"); library(formattable)}

#________________________________________________________________________________#
# [x] Define custom 'formatter's

## define custom colour set
customRed <- "#ff7f7f"
customGreen <- "#71CA97"
customGreen0 <- "#DeF7E9"

## [1] green tick yes/ red cross no
formatter_ticks <- formatter("span",
                             style = x ~ style(
                               color = ifelse(x, "green", "red")
                             ),
                             x ~ icontext(ifelse(x, "ok", "remove"), ifelse(x, "Yes", "No"))
)

## [2] green arrow up/ red arrow down
formatter_arrows <- formatter("span",
                              style = x ~ style(
                                font.weight = "bold",
                                color = ifelse(x > 0, customGreen, ifelse(x < 0, customRed, "black"))
                              ),
                              x ~ icontext(ifelse(x > 0, "arrow-up", "arrow-down"), x)
)

## [3] pink bar currency (Rxx,xxx,xxx.xx)
formatter_bars_curr <- formatter("span",
                                 style = x ~ style(
                                   display = "inline-block",
                                   direction = "rtl",
                                   "border-radius" = "4px",
                                   "padding-right" = "2px",
                                   "background-color" = csscolor("pink"),
                                   width = percent(proportion(as.numeric(gsub("R", "", gsub(",", "", x)))))
                                 )
)

## [4] status code green red (200, 4xx)
formatter_bars_code <- formatter("span",
                                 style = x ~ style(
                                   display = "inline-block",
                                   direction = "rtl",
                                   "border-radius" = "4px",
                                   "padding-right" = "2px",
                                   "background-color" = csscolor(ifelse(x==200, "lightgreen", "pink")),
                                   width = x
                                 )
)

## [4] images/ icons

img_dir <- "www/img/" # MUST name 'img_dir'!

encode <- function(img_path, filename) {
  result <- sprintf("data:image/png;base64,%s", base64encode(paste0(img_path, filename)))
  return (result)
}

formatter_images <- formatter("img",
src = x ~ 
ifelse(x == "kra", encode(img_dir, "kra.png"), 
ifelse(x == "lun", encode(img_dir, "lun.png"),
ifelse(x == "val", encode(img_dir, "val.png"),
ifelse(x == "ice", encode(img_dir, "ice.png"),
ifelse(x == "alt", encode(img_dir, "alt.png"),
ifelse(x == "eur", encode(img_dir, "eur_bold.png"),       
ifelse(x == "btc", encode(img_dir, "btc.png"), 
ifelse(x == "eth", encode(img_dir, "eth.png"),
ifelse(x == "ltc", encode(img_dir, "ltc.png"),
ifelse(x == "xrp", encode(img_dir, "xrp.png"),
ifelse(x == "doge", encode(img_dir, "doge.png"),
ifelse(x == "dog", encode(img_dir, "doge.png"),
ifelse(x == "comp", encode(img_dir, "comp.png"),
ifelse(x == "com", encode(img_dir, "comp.png"),
ifelse(x == "dash", encode(img_dir, "dash.png"),
ifelse(x == "das", encode(img_dir, "dash.png"),
ifelse(x == "ada", encode(img_dir, "ada.png"),
ifelse(x == "dot", encode(img_dir, "dot.png"),
ifelse(x == "link", encode(img_dir, "link.png"),
ifelse(x == "lin", encode(img_dir, "link.png"),
ifelse(x == "trx", encode(img_dir, "trx.png"),
ifelse(x == "xmr", encode(img_dir, "xmr.png"),
ifelse(x == "usdt", encode(img_dir, "usdt.png"),
ifelse(x == "usd", encode(img_dir, "usdt.png"),
ifelse(x == "zec", encode(img_dir, "zec.png"),
ifelse(x == "bat", encode(img_dir, "bat.png"),
ifelse(x == "dai", encode(img_dir, "dai.png"),

ifelse(x == "bch", encode(img_dir, "bch.png"), encode(img_dir, "none.png"))
))))))))))))))))))))))))))),
width = 15, height = 15, NA
)
