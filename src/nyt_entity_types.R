library(rjson)
library(ggplot2)
library(ggplotthemr)
library(gridExtra)


ggthemr::ggthemr('sky')


plot_entity_cnt <- function(file_path, lab){
  type_counter <- fromJSON(file = file_path)
  
  x <- names(type_counter)
  cnt <- matrix(unlist(type_counter), nrow=2, byrow=F)
  data <- data.frame(x,t(cnt))
  
  relations <- c(x,x)
  cnt <- c(data$X1, data$X2)
  Entity <- c(rep('head',length(x)),rep('tail',length(x)))
  
  
  pdata <- data.frame(relations, cnt, Entity)
  
  p1 <- ggplot(pdata, aes(x=reorder(relations, cnt), y=cnt, fill=Entity)) + 
    geom_histogram(position="dodge", stat = 'identity') +
    #theme(axis.text.x=element_text(angle=0,size=10)) +
    coord_flip() +
    lab
    # scale_y_log10() +
    # labs(x = "Count", y = "Relations", title = fig_title,colour = "CUT")
  p1
}

p1 <- plot_entity_cnt("rel_entity_type.json", labs(x = "Count", y = "Relations", title = "Different entity types in each relation",colour = "CUT"))

p2 <- plot_entity_cnt("imba_set_count_path.json", labs(x = "Count", y = "Relations", title = "Imbalanced entity types",colour = "CUT"))

entity_types <- grid.arrange(p1, p2, ncol=2)

normalized_entity_types <- plot_entity_cnt("one_entity_stats.json", labs(x = "Count", y = "Relations", title = "Most normalized types", colour = "CUT"))
reverse_problem <- plot_entity_cnt("reverse_problem_path.json", labs(x = "Entity types", y = "Relations", title = "Reverse Problem", colour = "CUT"))

ggsave(entity_types, filename = 'Entities_in_rels.png', dpi=600, width = 25.8/3*2, height = 14.2/3*2)
ggsave(normalized_entity_types, filename = 'Normalized_entity_types.png', dpi=600, width = 25.8/3*2, height = 14.2/3*2)
ggsave(reverse_problem, filename = "reverse_problem.png", dpi=600, width = 25.8/3*2, height = 14.2/3*2)