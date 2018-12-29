library(rjson)
library(ggplot2)
library(ggplotthemr)
library(gridExtra)


ggthemr::ggthemr('sky')


plot_entity_cnt <- function(file_path, fig_title){
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
    # scale_y_log10() +
    labs(x = "Count", y = "Relations", title = fig_title,colour = "CUT")
  p1
}

p1 <- plot_entity_cnt("rel_entity_type.json", "Different entity types in each relation")
p2 <- plot_entity_cnt("imba_set_count_path.json", "Imbalanced entity types")
entity_types <- grid.arrange(p1, p2, ncol=2)
normalized_entity_types <- plot_entity_cnt("one_entity_stats.json", "Most normalized types")
ggsave(entity_types, filename = 'Entities_in_rels.png', dpi=600, width = 25.8/3*2, height = 14.2/3*2)
ggsave(normalized_entity_types, filename = 'Normalized_entity_types.png', dpi=600, width = 25.8/3*2, height = 14.2/3*2)
