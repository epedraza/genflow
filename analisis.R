require("MASS")
require("pegas")
require("adegenet")
require("ggplot2")

DATADIR = './data'

parse_gametes <- function(df.gametes) {
  nloci <- nchar(df.gametes[[1,1]])
  size <- nrow(df.gametes)
  g1 <- strsplit(df.gametes[,1], "")
  g2 <- strsplit(df.gametes[,2], "")
  mt <- matrix(nrow=size,ncol=nloci)
  for (i in 1:size) 
    mt[i,] <- paste(g1[[i]], g2[[i]], sep="/")
  df <- data.frame(mt)
  colnames(df) <- paste0(rep("l", nloci), 1:nloci)
  return(df)
}

load_data <- function(filename) { 
  data <- read.csv(filename, header=T, stringsAsFactors = F)
  colnames(data) <- tolower(colnames(data))
  return(data)
}


parse_data <- function(data) {
  gametes <- c('gamete1', 'gamete2')
  genotypes <- parse_gametes(data[gametes])
  individuals <- df2genind(genotypes, ploidy=2, sep="/", ind.names = data[,'agentid'])
  data$subpop <- subpopulations(data[,c('x', 'y')], 3)
  strata(individuals) <- data[setdiff(names(data), gametes)]
  setPop(individuals) <- ~subpop
  return(individuals)
}

subpopulations <- function(positions, n) {
  # subdivide the square in nxn subsquares
  # positions is a data frame with x and y columns
  width <- (max(positions$x) + 1) / n
  height <- (max(positions$y) + 1) / n
  subpops <- paste(positions$x %/% width, positions$y %/% height, sep=".")
  return(subpops)
}

genetic_distance <- function() {
  # old function to plot genetic distance vs geografic distance
  # currently is broken :-(, some adaptions are need to 
  # run with the new data
  for (generation in generations) {
    population <- subset(data, population==generation)
    
    individuals <- df2genind(population[,5:(4+nloci)], ploidy=2, sep="/", ind.names=population[,"individual"], loc.names=lnames)
    positions <- population[,c('x', 'y')]
    rownames(positions) <- population[, "individual"]
    dis_geo = dist(positions)
    dis_gen = dist(individuals@tab)
    #plot(dis_geo, dis_gen)
    #abline(lm(dis_gen~dis_geo), col="red",lty=2)
    
    filename = sprintf("images/%04d.png" , generation)
    ptitle = sprintf("Isolation by distance (generation = %d)", generation)
    
    png(filename, width=800, height=600, res=150)
    plot(dis_geo, dis_gen, pch=20,cex=.5, xlim=c(0,120), ylim=c(0,8), xlab="Geographical distance", ylab="Genetic distance")
    if (generation > 0) {
      dens <- MASS::kde2d(dis_geo,dis_gen, n=50)
      myPal <- colorRampPalette(c("white","blue","gold", "orange", "red"))
      image(dens, col=transp(myPal(50),.7), add=TRUE)
      abline(lm(dis_gen~dis_geo),lty=2, lwd=2)
    }
    title(ptitle)
    dev.off()
  }
}

get_generation <- function(data, generation) {
  population <- subset(data, population==generation)
  individuals <- df2genind(population[,5:(4+nloci)], ploidy=2, sep="/", ind.names=population[,"individual"], loc.names=lnames)
  strata(individuals) <- data.frame(population=paste(population$x%/%20, population$y%/%20, sep=""))
  setPop(individuals) <-  ~population
  return(individuals)
}

get_fstats <- function(data) {
  generations <- unique(data$step)
  total <- length(generations)
  nloci <- nchar(data[1, c('gamete1')])
  mdata <- matrix(nrow=total*nloci, ncol=3)
  row = 0
  for (g in 1:total) {
    generation <- generations[g]
    ng <- as.integer(generation)
    individuals <- parse_data(data[data$step==generation,])
    results <- Fst(as.loci(individuals))
    for (l in 1:nloci) {
      row <- row + 1
      mdata[row,] <- c(ng, l ,results[l,c('Fst')] )
    } 
  }
  dt <- data.frame(mdata)
  colnames(dt) <- c('step', 'loci', 'fst')
  return(dt)
}

# function from
# http://www.sthda.com/english/wiki/ggplot2-error-bars-quick-start-guide-r-software-and-data-visualization

data_summary <- function(data, varname, groupnames){
  require(plyr)
  summary_func <- function(x, col){
    c(mean = mean(x[[col]], na.rm=TRUE),
      sd = sd(x[[col]], na.rm=TRUE))
  }
  data_sum<-ddply(data, groupnames, .fun=summary_func,
                  varname)
  data_sum <- rename(data_sum, c("mean" = varname))
  return(data_sum)
}




list_files <- function(pattern="ex01.*") {
  files <- list.files(DATADIR, pattern)
  lfiles <- strsplit(files, '_')
  mfiles <- matrix(nrow=length(lfiles), ncol=length(lfiles[[1]]))
  for (i in 1:length(lfiles))
    mfiles[i,] <- lfiles[[i]]
  df.files <- data.frame(mfiles)
  colnames(df.files) <- c('exp', 'square', 'steps', 'size', 'dispertion', 'coverage', 'type', 'rep1')
  rep1 <- strsplit(as.character(df.files$rep1), "\\.")
  df.files$rep <- as.factor(sapply(rep1, '[', 1))
  df.files$original <- files
  names <- data.frame(name=c('random-cluster','random'), values=c('ex01', 'ex02'))
  get_name <- function(exp) names[exp, c('name')]
  df.files$name <- sapply(df.files$exp, get_name)
  return(df.files)
}


parse_experiment <- function(pattern='ex0.*'){
  df.files <- list_files(pattern)
  total <- length(df.files$exp)
  df.all <- data.frame()
  for (i in 1:total) {
    filename <- file.path(DATADIR, df.files$original[i])
    data <- load_data(filename)
    fstats <- get_fstats(data)
    df.stats <- data_summary(fstats, varname = "fst", groupnames = c("step"))
    ngen <- length(df.stats$step) 
    df.stats$rep <- rep(df.files$rep[i], ngen)
    df.stats$coverage <- rep(df.files$coverage[i], ngen)
    df.stats$exp <- rep(df.files$exp[i], ngen)
    df.stats$name <- rep(df.files$name[i], ngen)
    df.all <- rbind(df.all, df.stats)
  }
  return(df.all)
}


plot_fstats <- function(stats, coverage=c(10,50,90)) {
  # change of Fst in the time among distinct percentage of
  # land coverage and land coverage arquitecture
  p <- ggplot(stats[stats$coverage %in% coverage,], aes(x=step,y=fst, group=rep, color=rep)) + geom_line() +
    geom_point() + geom_errorbar(aes(ymin=fst-sd,ymax=fst+sd), width=0.2) + facet_grid(coverage ~ name) +
    labs(y="Fst", x="Generaciones") + theme_bw()
  return(p) 
}


plot_fstats2 <- function(stats, steps=c(1000, 500, 50)) {
  p <- ggplot(stats[stats$step %in% steps,], aes(x=coverage,y=fst, group=rep, color=rep)) + geom_line() +
    geom_point() + geom_errorbar(aes(ymin=fst-sd,ymax=fst+sd), width=0.1) + facet_grid(step ~ exp)
  return(p) 
}

save_plot <- function(plot, name) {

  ggsave(name, plot=plot, device="png", width=6, height=8, units="in", dpi=300)
}

plot_experiment -> function() {
  # take some time to load all data into the data.frame d1 :-(
  d1 <- parse_experiment()
  p1 <- plot_fstats(d1, c(10, 30, 50, 70, 90))
  print(p1)
}
