# relation(train | test) - relation(train)
library(rjson)
library(ggplot2)
library(ggplotthemr)
library(gridExtra)

ggthemr::ggthemr('chalk')

rel_counter <- fromJSON(file = "rel_counter.json")

x <- names(rel_counter)
y <- (as.vector(unlist(rel_counter)))
data <- data.frame(x,y)
data <- data[order(data$y),]

test_exclusive_rel_c <- c(
  '/business/company/industry', 
  '/sports/sports_team_location/teams', 
  '/business/company_shareholder/major_shareholder_of', 
  '/people/ethnicity/people', 
  '/people/ethnicity/includes_groups'
)

test_exclusive_rel <- subset(data, data$x %in% test_exclusive_rel_c)

p1 <- ggplot(data, aes(x=reorder(x, -y),y=y)) + 
    geom_histogram(stat = 'identity') + 
    #theme(axis.text.x=element_text(angle=0,size=10)) +
    coord_flip() +
    scale_y_log10() +
    labs(x = "Count", y = "Relations", title = "All relations in train/test set",colour = "CUT")


p2 <- ggplot(data[1:10,], aes(x=reorder(x, -y),y=y, fill=y)) + 
    geom_histogram(stat="identity") + 
    #theme(axis.text.x=element_text(angle=0,size=10)) +
    coord_flip() +
    # scale_y_log10() +
    labs(x = "Count", y = "Relations", title = "The ten least relations",colour = "CUT")


p3 <- ggplot(data[46:56,], aes(x=reorder(x, -y),y=y, fill=y)) + 
    geom_histogram(stat="identity") + 
    #theme(axis.text.x=element_text(angle=0,size=10)) +
    coord_flip() +
    # scale_y_log10()+
    labs(x = "Count", y = "Relations", title = "The ten most relations",colour = "CUT")

p4 <- ggplot(test_exclusive_rel, aes(x=reorder(x, -y), y=y, fill=y)) +
  geom_histogram(stat="identity") + 
  coord_flip() +
  labs(x = "Count", y = "Relations", title = "Exclusive relations in test set",colour = "CUT")


relation_overview <- grid.arrange(p1, arrangeGrob(p3, p2, p4, nrow = 3), ncol=2)
# ggsave(relation_overview, filename = 'relation_overview.png', dpi=600, width = 25.8/3*2, height = 14.2/3*2)
