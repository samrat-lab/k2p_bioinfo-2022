# konnect2prot: a web application to explore the protein properties in a functional protein–protein interaction network
## Shivam Kumar, Dipanka Tanu Sarmah, Shailendra Asthana, Samrat Chatterjee

### Motivation
The regulation of proteins governs the biological processes and functions and, therefore, the organisms’ phenotype. So there is an unmet need for a systematic tool for identifying the proteins that play a crucial role in information processing in a protein–protein interaction (PPI) network. However, the current protein databases and web servers still lag behind to provide an end-to-end pipeline that can leverage the topological understanding of a context-specific PPI network to identify the influential spreaders. Addressing this, we developed a web application, ‘konnect2prot’ (k2p), which can generate context-specific directional PPI network from the input proteins and detect their biological and topological importance in the network.

### Results
We pooled together a large amount of ontological knowledge, parsed it down into a functional network, and gained insight into the molecular underpinnings of the disease development by creating a one-stop junction for PPI data. k2p contains both local and global information about a protein, such as protein class, disease mutations, ligands and PDB structure, enriched processes and pathways, multi-disease interactome and hubs and bottlenecks in the directional network. It also identifies spreaders in the network and maps them to disease hallmarks to determine whether they can affect the disease state or not.


# Usage
* Install packages using requirements.txt
* use command "python app.py" in code directory to run the application.

# Dataset

The dataset is availble on request from the corresponding author.

# Citation

Please cite our paper:

```
@article{kumar2023konnect2prot,
  title={konnect2prot: a web application to explore the protein properties in a functional protein--protein interaction network},
  author={Kumar, Shivam and Sarmah, Dipanka Tanu and Asthana, Shailendra and Chatterjee, Samrat},
  journal={Bioinformatics},
  volume={39},
  number={1},
  pages={btac815},
  year={2023},
  publisher={Oxford University Press}
}
```
